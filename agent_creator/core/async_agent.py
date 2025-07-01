"""
Async Base Agent - Base class for asynchronous agent operations
Enables parallel processing and async/await patterns
"""

import asyncio
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Coroutine
from datetime import datetime
from dataclasses import dataclass, field

from .base_agent import BaseAgent, AgentConfig, AgentTask
from .agent_bus import AgentBus, AgentEvent, EventType, get_agent_bus

@dataclass
class AsyncAgentTask(AgentTask):
    """Extended task class for async operations"""
    callback: Optional[Callable] = None
    priority: int = 0
    max_parallel: int = 1
    dependencies: List[str] = field(default_factory=list)

class AsyncBaseAgent(BaseAgent):
    """
    Async version of BaseAgent with parallel processing capabilities
    """
    
    def __init__(self, config: AgentConfig, agent_bus: Optional[AgentBus] = None):
        """
        Initialize async agent
        
        Args:
            config: Agent configuration
            agent_bus: Agent bus for communication
        """
        super().__init__(config)
        self.agent_bus = agent_bus or get_agent_bus()
        
        # Async task management
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.max_concurrent_tasks = config.max_retries or 5
        self.task_semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # Event handling
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        
        # Start background task processor
        self._task_processor_task = None
        
    async def start_async(self):
        """Start async agent operations"""
        self.start()
        
        # Subscribe to agent bus events
        await self._setup_event_subscriptions()
        
        # Start task processor
        self._task_processor_task = asyncio.create_task(self._process_tasks())
        
        self.logger.info(f"Async agent {self.config.name} started")
    
    async def stop_async(self):
        """Stop async agent operations"""
        self.stop()
        
        # Cancel task processor
        if self._task_processor_task:
            self._task_processor_task.cancel()
            try:
                await self._task_processor_task
            except asyncio.CancelledError:
                pass
        
        # Cancel running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        # Unsubscribe from events
        await self.agent_bus.unsubscribe(self.agent_id)
        
        self.logger.info(f"Async agent {self.config.name} stopped")
    
    async def _setup_event_subscriptions(self):
        """Setup event subscriptions on the agent bus"""
        # Subscribe to task events
        await self.agent_bus.subscribe(
            self.agent_id,
            [EventType.TASK_CREATED, EventType.TASK_COMPLETED, EventType.TASK_FAILED],
            self._handle_task_event
        )
        
        # Register request handlers
        await self.agent_bus.register_request_handler(
            self.agent_id,
            "execute_task",
            self._handle_task_request
        )
    
    async def _handle_task_event(self, event: AgentEvent):
        """Handle task-related events"""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
    
    async def _handle_task_request(self, request):
        """Handle task execution requests from other agents"""
        try:
            task_data = request.payload
            task = AsyncAgentTask(
                task_id=str(uuid.uuid4()),
                description=task_data.get("description", ""),
                parameters=task_data.get("parameters", {})
            )
            
            result = await self.execute_task_async(task)
            
            await self.agent_bus.send_response({
                "request_id": request.request_id,
                "source_agent_id": self.agent_id,
                "success": True,
                "payload": {"result": result}
            })
            
        except Exception as e:
            await self.agent_bus.send_response({
                "request_id": request.request_id,
                "source_agent_id": self.agent_id,
                "success": False,
                "error": str(e)
            })
    
    def subscribe_to_events(self, event_types: List[EventType], handler: Callable):
        """
        Subscribe to specific event types
        
        Args:
            event_types: List of event types to subscribe to
            handler: Handler function for events
        """
        for event_type in event_types:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(handler)
    
    async def create_task_async(self, description: str, parameters: Optional[Dict[str, Any]] = None, priority: int = 0) -> str:
        """
        Create async task
        
        Args:
            description: Task description
            parameters: Task parameters
            priority: Task priority (higher = more important)
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = AsyncAgentTask(
            task_id=task_id,
            description=description,
            parameters=parameters or {},
            priority=priority
        )
        
        self.tasks[task_id] = task
        
        # Add to task queue
        await self.task_queue.put(task)
        
        # Publish task created event
        await self.agent_bus.publish(AgentEvent(
            event_type=EventType.TASK_CREATED,
            source_agent_id=self.agent_id,
            payload={
                "task_id": task_id,
                "description": description,
                "priority": priority
            }
        ))
        
        self.logger.info(f"Created async task {task_id}: {description}")
        return task_id
    
    async def _process_tasks(self):
        """Background task processor"""
        while True:
            try:
                # Get task from queue
                task = await self.task_queue.get()
                
                # Create async task for execution
                execution_task = asyncio.create_task(self._execute_task_with_semaphore(task))
                self.running_tasks[task.task_id] = execution_task
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
    
    async def _execute_task_with_semaphore(self, task: AsyncAgentTask):
        """Execute task with concurrency control"""
        async with self.task_semaphore:
            try:
                task.status = "running"
                
                # Publish task started event
                await self.agent_bus.publish(AgentEvent(
                    event_type=EventType.TASK_STARTED,
                    source_agent_id=self.agent_id,
                    payload={"task_id": task.task_id}
                ))
                
                # Execute task
                result = await self.execute_task_async(task)
                task.result = result
                task.status = "completed"
                
                # Publish task completed event
                await self.agent_bus.publish(AgentEvent(
                    event_type=EventType.TASK_COMPLETED,
                    source_agent_id=self.agent_id,
                    payload={
                        "task_id": task.task_id,
                        "result": result
                    }
                ))
                
                # Call callback if provided
                if task.callback:
                    try:
                        if asyncio.iscoroutinefunction(task.callback):
                            await task.callback(result)
                        else:
                            task.callback(result)
                    except Exception as e:
                        self.logger.error(f"Error in task callback: {e}")
                
            except Exception as e:
                task.error = str(e)
                task.status = "failed"
                
                # Publish task failed event
                await self.agent_bus.publish(AgentEvent(
                    event_type=EventType.TASK_FAILED,
                    source_agent_id=self.agent_id,
                    payload={
                        "task_id": task.task_id,
                        "error": str(e)
                    }
                ))
                
                self.logger.error(f"Task {task.task_id} failed: {e}")
            
            finally:
                # Remove from running tasks
                self.running_tasks.pop(task.task_id, None)
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed async tasks"""
        completed_task_ids = []
        for task_id, task in self.running_tasks.items():
            if task.done():
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            self.running_tasks.pop(task_id, None)
    
    @abstractmethod
    async def execute_task_async(self, task: AsyncAgentTask) -> Any:
        """
        Execute async task - must be implemented by subclasses
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        pass
    
    async def run_task_async(self, task_id: str) -> Any:
        """
        Run task asynchronously
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        # If task is already running, wait for it
        if task_id in self.running_tasks:
            await self.running_tasks[task_id]
        else:
            # Execute task immediately
            await self._execute_task_with_semaphore(task)
        
        if task.status == "failed":
            raise RuntimeError(task.error)
        
        return task.result
    
    async def run_tasks_parallel(self, task_ids: List[str]) -> List[Any]:
        """
        Run multiple tasks in parallel
        
        Args:
            task_ids: List of task IDs to run
            
        Returns:
            List of task results
        """
        tasks = []
        for task_id in task_ids:
            tasks.append(self.run_task_async(task_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to proper errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise result
        
        return results
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for task completion
        
        Args:
            task_id: Task ID to wait for
            timeout: Timeout in seconds
            
        Returns:
            Task result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        # If not running, start it
        if task_id not in self.running_tasks and task.status == "pending":
            await self.task_queue.put(task)
        
        # Wait for completion
        start_time = asyncio.get_event_loop().time()
        while task.status in ["pending", "running"]:
            if timeout and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise asyncio.TimeoutError(f"Task {task_id} timed out")
            
            await asyncio.sleep(0.1)
        
        if task.status == "failed":
            raise RuntimeError(task.error)
        
        return task.result
    
    async def cancel_task(self, task_id: str):
        """
        Cancel a running task
        
        Args:
            task_id: Task ID to cancel
        """
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        if task_id in self.tasks:
            self.tasks[task_id].status = "cancelled"
    
    def get_running_tasks(self) -> List[str]:
        """
        Get list of currently running task IDs
        
        Returns:
            List of running task IDs
        """
        return list(self.running_tasks.keys())
    
    def get_queue_size(self) -> int:
        """
        Get current task queue size
        
        Returns:
            Number of queued tasks
        """
        return self.task_queue.qsize()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_async()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_async()