"""
Agent Bus - Central message bus for agent communication
Implements event-driven architecture and pub/sub patterns
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

class EventType(Enum):
    """Event types for agent communication"""
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    CUSTOM = "custom"

@dataclass
class AgentEvent:
    """Event for agent communication"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CUSTOM
    source_agent_id: str = ""
    target_agent_id: Optional[str] = None  # None for broadcast
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None

@dataclass
class AgentRequest:
    """Request for agent communication"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_agent_id: str = ""
    target_agent_id: str = ""
    request_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass 
class AgentResponse:
    """Response for agent communication"""
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    source_agent_id: str = ""
    success: bool = True
    payload: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class AgentBus:
    """
    Central message bus for agent communication
    Supports pub/sub patterns and request/response communication
    """
    
    def __init__(self):
        """Initialize the agent bus"""
        self.logger = logging.getLogger(__name__)
        
        # Subscribers: event_type -> set of (agent_id, callback)
        self.subscribers: Dict[EventType, Set[tuple]] = {}
        
        # Request handlers: request_type -> (agent_id, callback)
        self.request_handlers: Dict[str, tuple] = {}
        
        # Pending requests for request/response pattern
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
        # Event history for debugging
        self.event_history: List[AgentEvent] = []
        self.max_history_size = 1000
        
        # Statistics
        self.stats = {
            "events_published": 0,
            "requests_sent": 0,
            "responses_sent": 0,
            "active_subscribers": 0
        }
    
    async def publish(self, event: AgentEvent):
        """
        Publish event to interested agents
        
        Args:
            event: Event to publish
        """
        self.logger.debug(f"Publishing event {event.event_type} from {event.source_agent_id}")
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Update stats
        self.stats["events_published"] += 1
        
        # Get subscribers for this event type
        subscribers = self.subscribers.get(event.event_type, set())
        
        # If target_agent_id is specified, filter subscribers
        if event.target_agent_id:
            subscribers = {(agent_id, callback) for agent_id, callback in subscribers 
                         if agent_id == event.target_agent_id}
        
        # Notify subscribers
        tasks = []
        for agent_id, callback in subscribers:
            if agent_id != event.source_agent_id:  # Don't send to self
                tasks.append(self._notify_subscriber(callback, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _notify_subscriber(self, callback: Callable, event: AgentEvent):
        """Notify a single subscriber about an event"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            self.logger.error(f"Error notifying subscriber: {e}")
    
    async def subscribe(self, agent_id: str, event_types: List[EventType], callback: Callable):
        """
        Subscribe agent to specific event types
        
        Args:
            agent_id: ID of the subscribing agent
            event_types: List of event types to subscribe to
            callback: Callback function to handle events
        """
        for event_type in event_types:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = set()
            
            self.subscribers[event_type].add((agent_id, callback))
        
        self.stats["active_subscribers"] = sum(len(subs) for subs in self.subscribers.values())
        self.logger.info(f"Agent {agent_id} subscribed to {len(event_types)} event types")
    
    async def unsubscribe(self, agent_id: str, event_types: Optional[List[EventType]] = None):
        """
        Unsubscribe agent from event types
        
        Args:
            agent_id: ID of the agent
            event_types: Event types to unsubscribe from (None for all)
        """
        if event_types is None:
            # Unsubscribe from all event types
            for event_type in self.subscribers:
                self.subscribers[event_type] = {
                    (aid, cb) for aid, cb in self.subscribers[event_type] 
                    if aid != agent_id
                }
        else:
            # Unsubscribe from specific event types
            for event_type in event_types:
                if event_type in self.subscribers:
                    self.subscribers[event_type] = {
                        (aid, cb) for aid, cb in self.subscribers[event_type]
                        if aid != agent_id
                    }
        
        self.stats["active_subscribers"] = sum(len(subs) for subs in self.subscribers.values())
        self.logger.info(f"Agent {agent_id} unsubscribed")
    
    async def request_response(self, request: AgentRequest) -> AgentResponse:
        """
        Request-response pattern for agent communication
        
        Args:
            request: Request to send
            
        Returns:
            Response from target agent
        """
        self.logger.debug(f"Sending request {request.request_type} from {request.source_agent_id} to {request.target_agent_id}")
        
        # Update stats
        self.stats["requests_sent"] += 1
        
        # Check if handler exists
        if request.request_type not in self.request_handlers:
            raise ValueError(f"No handler registered for request type: {request.request_type}")
        
        handler_agent_id, handler_callback = self.request_handlers[request.request_type]
        
        # Check if target agent matches (if specified)
        if request.target_agent_id and handler_agent_id != request.target_agent_id:
            raise ValueError(f"Request target {request.target_agent_id} does not match handler agent {handler_agent_id}")
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_requests[request.request_id] = response_future
        
        try:
            # Call handler
            if asyncio.iscoroutinefunction(handler_callback):
                await handler_callback(request)
            else:
                handler_callback(request)
            
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=request.timeout)
            return response
            
        except asyncio.TimeoutError:
            self.logger.error(f"Request {request.request_id} timed out")
            raise
        except Exception as e:
            self.logger.error(f"Request {request.request_id} failed: {e}")
            raise
        finally:
            # Clean up
            self.pending_requests.pop(request.request_id, None)
    
    async def send_response(self, response: AgentResponse):
        """
        Send response to a pending request
        
        Args:
            response: Response to send
        """
        self.logger.debug(f"Sending response for request {response.request_id}")
        
        # Update stats
        self.stats["responses_sent"] += 1
        
        # Find pending request
        if response.request_id in self.pending_requests:
            future = self.pending_requests[response.request_id]
            if not future.done():
                future.set_result(response)
        else:
            self.logger.warning(f"No pending request found for response {response.request_id}")
    
    async def register_request_handler(self, agent_id: str, request_type: str, callback: Callable):
        """
        Register handler for request type
        
        Args:
            agent_id: ID of the handling agent
            request_type: Type of request to handle
            callback: Callback function to handle requests
        """
        if request_type in self.request_handlers:
            self.logger.warning(f"Overriding existing handler for request type: {request_type}")
        
        self.request_handlers[request_type] = (agent_id, callback)
        self.logger.info(f"Registered handler for {request_type} with agent {agent_id}")
    
    async def unregister_request_handler(self, agent_id: str, request_type: str):
        """
        Unregister handler for request type
        
        Args:
            agent_id: ID of the agent
            request_type: Type of request to unregister
        """
        if request_type in self.request_handlers:
            handler_agent_id, _ = self.request_handlers[request_type]
            if handler_agent_id == agent_id:
                del self.request_handlers[request_type]
                self.logger.info(f"Unregistered handler for {request_type}")
    
    def get_event_history(self, limit: Optional[int] = None) -> List[AgentEvent]:
        """
        Get event history
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        if limit:
            return self.event_history[-limit:]
        return self.event_history.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get bus statistics
        
        Returns:
            Dictionary of statistics
        """
        return {
            **self.stats,
            "pending_requests": len(self.pending_requests),
            "registered_handlers": len(self.request_handlers),
            "event_types_subscribed": len(self.subscribers),
            "event_history_size": len(self.event_history)
        }
    
    def clear_history(self):
        """Clear event history"""
        self.event_history.clear()
    
    def reset_statistics(self):
        """Reset statistics"""
        self.stats = {
            "events_published": 0,
            "requests_sent": 0, 
            "responses_sent": 0,
            "active_subscribers": sum(len(subs) for subs in self.subscribers.values())
        }

# Global agent bus instance
_global_agent_bus = None

def get_agent_bus() -> AgentBus:
    """Get the global agent bus instance"""
    global _global_agent_bus
    if _global_agent_bus is None:
        _global_agent_bus = AgentBus()
    return _global_agent_bus

def set_agent_bus(bus: AgentBus):
    """Set the global agent bus instance"""
    global _global_agent_bus
    _global_agent_bus = bus