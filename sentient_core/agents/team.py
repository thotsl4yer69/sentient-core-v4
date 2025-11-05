"""
Agent team coordination and collaboration system.
"""

import logging
from typing import Dict, Any, Optional, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .base_agent import BaseAgent
from .specialized_agents import (
    ResearchAgent,
    AnalysisAgent,
    ExecutionAgent,
    CoordinatorAgent
)


logger = logging.getLogger(__name__)


class AgentTeam:
    """
    Manages a team of agents working together on complex tasks.

    The team can dynamically create agents, assign tasks, and coordinate
    their activities to achieve complex goals.
    """

    def __init__(self, config, model_manager=None):
        """
        Initialize agent team.

        Args:
            config: Configuration object
            model_manager: Optional model manager for agent reasoning
        """
        self.config = config
        self.model_manager = model_manager
        self.agents: List[BaseAgent] = []
        self.coordinator: Optional[CoordinatorAgent] = None
        self.task_history: List[Dict[str, Any]] = []
        self.executor = ThreadPoolExecutor(max_workers=10)

        logger.info("AgentTeam created")

    def initialize(self):
        """Initialize the agent team with default agents."""
        logger.info("Initializing agent team...")

        # Create coordinator
        self.coordinator = CoordinatorAgent(name="TeamCoordinator")
        self.coordinator.activate()

        # Create default specialized agents
        research_agent = ResearchAgent(name="ResearchSpecialist")
        analysis_agent = AnalysisAgent(name="AnalysisSpecialist")
        execution_agent = ExecutionAgent(name="ExecutionSpecialist")

        # Add to team
        self.add_agent(research_agent)
        self.add_agent(analysis_agent)
        self.add_agent(execution_agent)

        # Register with coordinator
        for agent in self.agents:
            self.coordinator.add_agent(agent)

        logger.info(f"Agent team initialized with {len(self.agents)} agents")

    def add_agent(self, agent: BaseAgent):
        """Add an agent to the team."""
        agent.activate()
        self.agents.append(agent)
        logger.info(f"Added agent to team: {agent.name}")

    def remove_agent(self, agent: BaseAgent):
        """Remove an agent from the team."""
        if agent in self.agents:
            agent.deactivate()
            self.agents.remove(agent)
            logger.info(f"Removed agent from team: {agent.name}")

    def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_agent_by_capability(self, capability: str) -> Optional[BaseAgent]:
        """Get an agent that has a specific capability."""
        for agent in self.agents:
            if agent.can_handle(capability):
                return agent
        return None

    def execute_task(self, task: str, num_agents: int = 3, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a complex task using the agent team.

        Args:
            task: Task description
            num_agents: Number of agents to involve
            context: Optional context information

        Returns:
            Aggregated task results
        """
        logger.info(f"Executing team task: {task}")

        # Record task
        task_record = {
            'task': task,
            'context': context,
            'num_agents': num_agents
        }

        # Use coordinator to plan task distribution
        if self.coordinator:
            coordination_plan = self.coordinator.process_task(
                f"Coordinate: {task}",
                context
            )
            task_record['plan'] = coordination_plan

        # Select agents for the task
        selected_agents = self._select_agents_for_task(task, num_agents)

        # Distribute task to agents
        agent_results = []
        for agent in selected_agents:
            try:
                result = agent.process_task(task, context)
                agent_results.append(result)
                logger.info(f"Agent {agent.name} completed task")
            except Exception as e:
                logger.error(f"Agent {agent.name} failed: {e}")
                agent_results.append({
                    'agent': agent.name,
                    'status': 'failed',
                    'error': str(e)
                })

        # Aggregate results
        aggregated_result = self._aggregate_results(task, agent_results)
        task_record['results'] = aggregated_result

        # Store in history
        self.task_history.append(task_record)

        return aggregated_result

    async def execute_task_async(self, task: str, num_agents: int = 3, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Async version of execute_task."""
        logger.info(f"Executing team task asynchronously: {task}")

        # Select agents
        selected_agents = self._select_agents_for_task(task, num_agents)

        # Execute tasks in parallel
        tasks = [
            asyncio.to_thread(agent.process_task, task, context)
            for agent in selected_agents
        ]

        agent_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for i, result in enumerate(agent_results):
            if isinstance(result, Exception):
                logger.error(f"Agent {selected_agents[i].name} failed: {result}")
                processed_results.append({
                    'agent': selected_agents[i].name,
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        return self._aggregate_results(task, processed_results)

    def _select_agents_for_task(self, task: str, num_agents: int) -> List[BaseAgent]:
        """
        Select appropriate agents for a task.

        Args:
            task: Task description
            num_agents: Number of agents to select

        Returns:
            List of selected agents
        """
        # Simple selection: use first N active agents
        # In a real implementation, this would use semantic matching
        active_agents = [agent for agent in self.agents if agent.active]

        selected = active_agents[:min(num_agents, len(active_agents))]

        if not selected:
            logger.warning("No active agents available, creating new ones")
            # Create temporary agents if needed
            temp_agent = ResearchAgent(name=f"TempAgent-{len(self.agents)}")
            temp_agent.activate()
            self.add_agent(temp_agent)
            selected = [temp_agent]

        logger.info(f"Selected {len(selected)} agents for task")
        return selected

    def _aggregate_results(self, task: str, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agents.

        Args:
            task: Original task
            agent_results: Results from each agent

        Returns:
            Aggregated result dictionary
        """
        successful_results = [r for r in agent_results if r.get('status') == 'completed']
        failed_results = [r for r in agent_results if r.get('status') == 'failed']

        aggregated = {
            'task': task,
            'total_agents': len(agent_results),
            'successful': len(successful_results),
            'failed': len(failed_results),
            'agent_results': agent_results,
            'summary': self._create_summary(successful_results),
            'status': 'completed' if successful_results else 'failed'
        }

        return aggregated

    def _create_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a summary from multiple agent results."""
        if not results:
            return "No successful results to summarize"

        # Combine findings from all agents
        summary_parts = []
        for result in results:
            agent_name = result.get('agent', 'Unknown')
            # Extract key information from each result
            if 'findings' in result:
                summary_parts.append(f"{agent_name}: {result['findings']}")
            elif 'analysis' in result:
                summary_parts.append(f"{agent_name}: {result['analysis']}")
            elif 'execution_log' in result:
                summary_parts.append(f"{agent_name}: {result['execution_log']}")

        return " | ".join(summary_parts)

    def get_team_status(self) -> Dict[str, Any]:
        """Get current team status."""
        return {
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents if a.active]),
            'agents': [agent.get_info() for agent in self.agents],
            'coordinator': self.coordinator.get_info() if self.coordinator else None,
            'tasks_completed': len(self.task_history)
        }

    def shutdown(self):
        """Shutdown the agent team."""
        logger.info("Shutting down agent team...")

        for agent in self.agents:
            agent.deactivate()

        if self.coordinator:
            self.coordinator.deactivate()

        self.executor.shutdown(wait=True)

        logger.info("Agent team shutdown complete")
