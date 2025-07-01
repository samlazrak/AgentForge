"""
Base Agent class for the Agent Creator framework
"""

import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from ..utils.llm_interface import LLMInterface, LLMConfig

@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    llm_config: Optional[LLMConfig] = None
    max_retries: int = 3
    timeout: int = 30

@dataclass
class AgentTask:
    """Represents a task for an agent"""
    task_id: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None

class BaseAgent(ABC):
    """
    Base class for all agents in the framework
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the base agent
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.agent_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"{__name__}.{self.config.name}")
        self.tasks: Dict[str, AgentTask] = {}
        self.is_running = False
        
        # Initialize LLM interface
        self.llm = LLMInterface(config.llm_config)
        
        # Agent-specific initialization
        self._initialize()
    
    def _initialize(self):
        """Override this method for agent-specific initialization"""
        pass
    
    @abstractmethod
    def execute_task(self, task: AgentTask) -> Any:
        """
        Execute a specific task
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        pass
    
    def create_task(self, description: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new task for the agent
        
        Args:
            description: Task description
            parameters: Task parameters
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            description=description,
            parameters=parameters or {}
        )
        self.tasks[task_id] = task
        self.logger.info(f"Created task {task_id}: {description}")
        return task_id
    
    def run_task(self, task_id: str) -> Any:
        """
        Run a specific task
        
        Args:
            task_id: ID of the task to run
            
        Returns:
            Task result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = "running"
        
        try:
            self.logger.info(f"Starting task {task_id}")
            result = self.execute_task(task)
            task.result = result
            task.status = "completed"
            self.logger.info(f"Completed task {task_id}")
            return result
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            self.logger.error(f"Task {task_id} failed: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "result": task.result,
            "error": task.error
        }
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all tasks for this agent
        
        Returns:
            List of task information
        """
        return [self.get_task_status(task_id) for task_id in self.tasks.keys()]
    
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List of capabilities
        """
        return self.config.capabilities.copy()
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent
        
        Returns:
            Agent information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "description": self.config.description,
            "capabilities": self.config.capabilities,
            "is_running": self.is_running,
            "task_count": len(self.tasks),
            "llm_info": self.llm.get_model_info()
        }
    
    def start(self):
        """Start the agent"""
        self.is_running = True
        self.logger.info(f"Agent {self.config.name} started")
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.logger.info(f"Agent {self.config.name} stopped")
        
    def __str__(self) -> str:
        return f"Agent({self.config.name}, {self.agent_id})"
    
    def __repr__(self) -> str:
        return self.__str__()