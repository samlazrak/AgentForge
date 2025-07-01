"""
Core modules for the Agent Creator framework
"""

from .base_agent import BaseAgent, AgentConfig, AgentTask

# Import new infrastructure components
try:
    from .agent_bus import AgentBus, AgentEvent, AgentRequest, AgentResponse
except ImportError:
    AgentBus = AgentEvent = AgentRequest = AgentResponse = None

try:
    from .agent_registry import AgentRegistry
except ImportError:
    AgentRegistry = None

try:
    from .async_agent import AsyncBaseAgent
except ImportError:
    AsyncBaseAgent = None

__all__ = ["BaseAgent", "AgentConfig", "AgentTask"]

# Add to __all__ if successfully imported
if AgentBus is not None:
    __all__.extend(["AgentBus", "AgentEvent", "AgentRequest", "AgentResponse"])

if AgentRegistry is not None:
    __all__.append("AgentRegistry")

if AsyncBaseAgent is not None:
    __all__.append("AsyncBaseAgent")