"""
Agent Registry - Registry for dynamic agent discovery and management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Type, Callable
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from .base_agent import BaseAgent, AgentConfig
from .agent_bus import AgentBus, AgentEvent, EventType, get_agent_bus

@dataclass
class AgentCapability:
    """Represents an agent capability"""
    name: str
    description: str
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)

@dataclass
class AgentRegistration:
    """Registration information for an agent"""
    agent_id: str
    agent_name: str
    agent_type: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    status: str = "registered"  # registered, active, inactive, error
    instance: Optional[BaseAgent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

@dataclass 
class WorkflowStep:
    """Single step in a workflow"""
    step_id: str
    agent_capability: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    parallel: bool = False

@dataclass
class WorkflowDefinition:
    """Definition of an agent workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

class AgentRegistry:
    """
    Registry for dynamic agent discovery and management
    Supports agent registration, capability-based discovery, and workflow creation
    """
    
    def __init__(self, agent_bus: Optional[AgentBus] = None):
        """
        Initialize the agent registry
        
        Args:
            agent_bus: Agent bus for communication (uses global if None)
        """
        self.logger = logging.getLogger(__name__)
        self.agent_bus = agent_bus or get_agent_bus()
        
        # Registry storage
        self.agents: Dict[str, AgentRegistration] = {}
        self.capabilities: Dict[str, Set[str]] = {}  # capability -> agent_ids
        self.agent_types: Dict[str, Type[BaseAgent]] = {}  # agent_type -> class
        
        # Workflow storage
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.running_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Subscribe to agent events
        asyncio.create_task(self._setup_event_subscriptions())
    
    async def _setup_event_subscriptions(self):
        """Setup event subscriptions"""
        await self.agent_bus.subscribe(
            "agent_registry",
            [EventType.AGENT_REGISTERED, EventType.AGENT_UNREGISTERED],
            self._handle_agent_event
        )
    
    async def _handle_agent_event(self, event: AgentEvent):
        """Handle agent-related events"""
        if event.event_type == EventType.AGENT_REGISTERED:
            agent_id = event.payload.get("agent_id")
            if agent_id in self.agents:
                self.agents[agent_id].last_seen = datetime.now()
        elif event.event_type == EventType.AGENT_UNREGISTERED:
            agent_id = event.payload.get("agent_id")
            if agent_id in self.agents:
                self.agents[agent_id].status = "inactive"
    
    async def register_agent(self, agent: BaseAgent, capabilities: Optional[List[AgentCapability]] = None) -> str:
        """
        Register agent with capabilities
        
        Args:
            agent: Agent instance to register
            capabilities: List of agent capabilities
            
        Returns:
            Registration ID
        """
        # Extract basic capabilities from agent config
        basic_capabilities = []
        if capabilities is None:
            capabilities = []
            for cap_name in agent.config.capabilities:
                capabilities.append(AgentCapability(
                    name=cap_name,
                    description=f"Capability: {cap_name}"
                ))
        
        # Create registration
        registration = AgentRegistration(
            agent_id=agent.agent_id,
            agent_name=agent.config.name,
            agent_type=type(agent).__name__,
            capabilities=capabilities,
            instance=agent,
            metadata={
                "description": agent.config.description,
                "config": agent.config.__dict__
            }
        )
        
        # Store registration
        self.agents[agent.agent_id] = registration
        
        # Index capabilities
        for capability in capabilities:
            if capability.name not in self.capabilities:
                self.capabilities[capability.name] = set()
            self.capabilities[capability.name].add(agent.agent_id)
        
        # Store agent type for factory creation
        self.agent_types[type(agent).__name__] = type(agent)
        
        self.logger.info(f"Registered agent {agent.config.name} ({agent.agent_id}) with {len(capabilities)} capabilities")
        
        # Publish registration event
        await self.agent_bus.publish(AgentEvent(
            event_type=EventType.AGENT_REGISTERED,
            source_agent_id="agent_registry",
            payload={
                "agent_id": agent.agent_id,
                "agent_name": agent.config.name,
                "capabilities": [cap.name for cap in capabilities]
            }
        ))
        
        return agent.agent_id
    
    async def unregister_agent(self, agent_id: str):
        """
        Unregister an agent
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        registration = self.agents[agent_id]
        
        # Remove from capability index
        for capability in registration.capabilities:
            if capability.name in self.capabilities:
                self.capabilities[capability.name].discard(agent_id)
                if not self.capabilities[capability.name]:
                    del self.capabilities[capability.name]
        
        # Remove registration
        del self.agents[agent_id]
        
        self.logger.info(f"Unregistered agent {registration.agent_name} ({agent_id})")
        
        # Publish unregistration event
        await self.agent_bus.publish(AgentEvent(
            event_type=EventType.AGENT_UNREGISTERED,
            source_agent_id="agent_registry",
            payload={
                "agent_id": agent_id,
                "agent_name": registration.agent_name
            }
        ))
    
    def find_agents_by_capability(self, capability: str) -> List[AgentRegistration]:
        """
        Find agents that provide specific capabilities
        
        Args:
            capability: Capability name to search for
            
        Returns:
            List of agent registrations
        """
        if capability not in self.capabilities:
            return []
        
        agent_ids = self.capabilities[capability]
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def find_agents_by_type(self, agent_type: str) -> List[AgentRegistration]:
        """
        Find agents by type
        
        Args:
            agent_type: Agent type to search for
            
        Returns:
            List of agent registrations
        """
        return [reg for reg in self.agents.values() if reg.agent_type == agent_type]
    
    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """
        Get agent registration by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent registration or None
        """
        return self.agents.get(agent_id)
    
    def list_agents(self, status: Optional[str] = None) -> List[AgentRegistration]:
        """
        List all registered agents
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            List of agent registrations
        """
        agents = list(self.agents.values())
        if status:
            agents = [agent for agent in agents if agent.status == status]
        return agents
    
    def list_capabilities(self) -> List[str]:
        """
        List all available capabilities
        
        Returns:
            List of capability names
        """
        return list(self.capabilities.keys())
    
    async def create_agent_instance(self, agent_type: str, config: AgentConfig) -> Optional[BaseAgent]:
        """
        Create new agent instance by type
        
        Args:
            agent_type: Type of agent to create
            config: Agent configuration
            
        Returns:
            Created agent instance or None
        """
        if agent_type not in self.agent_types:
            self.logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        try:
            agent_class = self.agent_types[agent_type]
            agent = agent_class(config)
            await self.register_agent(agent)
            return agent
        except Exception as e:
            self.logger.error(f"Failed to create agent of type {agent_type}: {e}")
            return None
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """
        Register a workflow definition
        
        Args:
            workflow: Workflow definition
        """
        self.workflows[workflow.workflow_id] = workflow
        self.logger.info(f"Registered workflow {workflow.name} ({workflow.workflow_id})")
    
    async def create_agent_workflow(self, workflow_def: WorkflowDefinition, inputs: Dict[str, Any]) -> str:
        """
        Create and execute dynamic workflow from agent combinations
        
        Args:
            workflow_def: Workflow definition
            inputs: Input data for workflow
            
        Returns:
            Workflow execution ID
        """
        execution_id = str(uuid.uuid4())
        
        # Validate workflow
        if not self._validate_workflow(workflow_def):
            raise ValueError("Invalid workflow definition")
        
        # Create execution context
        execution_context = {
            "execution_id": execution_id,
            "workflow_def": workflow_def,
            "inputs": inputs,
            "outputs": {},
            "step_results": {},
            "status": "running",
            "started_at": datetime.now()
        }
        
        self.running_workflows[execution_id] = execution_context
        
        # Execute workflow asynchronously
        asyncio.create_task(self._execute_workflow(execution_context))
        
        return execution_id
    
    def _validate_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """
        Validate workflow definition
        
        Args:
            workflow_def: Workflow to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if all required capabilities are available
        for step in workflow_def.steps:
            agents = self.find_agents_by_capability(step.agent_capability)
            if not agents:
                self.logger.error(f"No agents found for capability: {step.agent_capability}")
                return False
        
        # Check dependency cycles
        # Simple check - more sophisticated cycle detection could be added
        step_ids = {step.step_id for step in workflow_def.steps}
        for step in workflow_def.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    self.logger.error(f"Invalid dependency {dep} in step {step.step_id}")
                    return False
        
        return True
    
    async def _execute_workflow(self, execution_context: Dict[str, Any]):
        """
        Execute workflow steps
        
        Args:
            execution_context: Workflow execution context
        """
        try:
            workflow_def = execution_context["workflow_def"]
            inputs = execution_context["inputs"]
            
            # Create execution plan based on dependencies
            execution_plan = self._create_execution_plan(workflow_def.steps)
            
            # Execute steps according to plan
            for step_group in execution_plan:
                if step_group:  # Parallel steps
                    tasks = []
                    for step in step_group:
                        tasks.append(self._execute_workflow_step(step, execution_context))
                    await asyncio.gather(*tasks)
                else:  # Sequential step
                    step = step_group[0]
                    await self._execute_workflow_step(step, execution_context)
            
            execution_context["status"] = "completed"
            execution_context["completed_at"] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            execution_context["status"] = "failed"
            execution_context["error"] = str(e)
    
    def _create_execution_plan(self, steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
        """
        Create execution plan respecting dependencies and parallelism
        
        Args:
            steps: Workflow steps
            
        Returns:
            List of step groups (parallel steps in each group)
        """
        # Simple implementation - can be enhanced with more sophisticated scheduling
        executed = set()
        plan = []
        
        while len(executed) < len(steps):
            # Find steps that can be executed (all dependencies met)
            ready_steps = []
            for step in steps:
                if step.step_id not in executed:
                    if all(dep in executed for dep in step.dependencies):
                        ready_steps.append(step)
            
            if not ready_steps:
                # Circular dependency or other issue
                break
            
            # Group parallel steps
            parallel_group = []
            sequential_steps = []
            
            for step in ready_steps:
                if step.parallel:
                    parallel_group.append(step)
                else:
                    sequential_steps.append(step)
            
            # Add parallel group if any
            if parallel_group:
                plan.append(parallel_group)
                executed.update(step.step_id for step in parallel_group)
            
            # Add sequential steps one by one
            for step in sequential_steps:
                plan.append([step])
                executed.add(step.step_id)
        
        return plan
    
    async def _execute_workflow_step(self, step: WorkflowStep, execution_context: Dict[str, Any]):
        """
        Execute a single workflow step
        
        Args:
            step: Workflow step to execute
            execution_context: Execution context
        """
        # Find suitable agent
        agents = self.find_agents_by_capability(step.agent_capability)
        if not agents:
            raise RuntimeError(f"No agents found for capability: {step.agent_capability}")
        
        # Select first available agent (could be enhanced with load balancing)
        agent_reg = agents[0]
        agent = agent_reg.instance
        
        if not agent:
            raise RuntimeError(f"Agent instance not available: {agent_reg.agent_id}")
        
        # Prepare step inputs
        step_inputs = {}
        for input_key, source_key in step.input_mapping.items():
            if source_key in execution_context["inputs"]:
                step_inputs[input_key] = execution_context["inputs"][source_key]
            elif source_key in execution_context["step_results"]:
                step_inputs[input_key] = execution_context["step_results"][source_key]
        
        # Execute step
        task_id = agent.create_task(f"workflow_step_{step.step_id}", {
            "type": step.agent_capability,
            **step_inputs
        })
        
        result = agent.run_task(task_id)
        
        # Store results
        execution_context["step_results"][step.step_id] = result
        
        # Map outputs
        for output_key, target_key in step.output_mapping.items():
            if hasattr(result, output_key):
                execution_context["outputs"][target_key] = getattr(result, output_key)
            elif isinstance(result, dict) and output_key in result:
                execution_context["outputs"][target_key] = result[output_key]
    
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow execution status
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Execution status or None
        """
        if execution_id not in self.running_workflows:
            return None
        
        context = self.running_workflows[execution_id]
        return {
            "execution_id": execution_id,
            "workflow_name": context["workflow_def"].name,
            "status": context["status"],
            "started_at": context["started_at"].isoformat(),
            "completed_at": context.get("completed_at", {}).isoformat() if context.get("completed_at") else None,
            "error": context.get("error"),
            "outputs": context.get("outputs", {})
        }
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics
        
        Returns:
            Dictionary of statistics
        """
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == "active"]),
            "total_capabilities": len(self.capabilities),
            "registered_workflows": len(self.workflows),
            "running_workflows": len(self.running_workflows),
            "agent_types": list(self.agent_types.keys())
        }

# Global agent registry instance
_global_agent_registry = None

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance"""
    global _global_agent_registry
    if _global_agent_registry is None:
        _global_agent_registry = AgentRegistry()
    return _global_agent_registry

def set_agent_registry(registry: AgentRegistry):
    """Set the global agent registry instance"""
    global _global_agent_registry
    _global_agent_registry = registry