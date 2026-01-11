"""Agent Executor for orchestrating concurrent agent execution."""

import asyncio
from typing import Dict

from src.state.academic_state import AcademicState
from src.agents.planner import PlannerAgent
from src.agents.notewriter import NoteWriterAgent
from src.agents.advisor import AdvisorAgent


class AgentExecutor:
    """Orchestrates concurrent execution of multiple AI agents."""

    def __init__(self, llm):
        """
        Initialize the executor with a language model and create agent instances.

        Args:
            llm: Language model instance to be used by all agents

        Implementation Note:
            - Creates a dictionary of specialized agents, each initialized with the same LLM
            - Supports multiple agent types: PLANNER (default), NOTEWRITER, and ADVISOR
            - Agents are instantiated once and reused across executions
        """
        self.llm = llm
        self.agents = {
            "PLANNER": PlannerAgent(llm),
            "NOTEWRITER": NoteWriterAgent(llm),
            "ADVISOR": AdvisorAgent(llm)
        }

    async def execute(self, state: AcademicState) -> Dict:
        """
        Orchestrates concurrent execution of multiple AI agents based on analysis results.

        This method implements a sophisticated execution pattern:
        1. Reads coordination analysis to determine required agents
        2. Groups agents for concurrent execution
        3. Executes agent groups in parallel
        4. Handles failures gracefully with fallback mechanisms

        Args:
            state (AcademicState): Current academic state containing analysis results

        Returns:
            Dict: Consolidated results from all executed agents
        """
        try:
            # Extract coordination analysis from state
            analysis = state["results"].get("coordinator_analysis", {})

            # Determine execution requirements
            required_agents = analysis.get("required_agents", ["PLANNER"])
            concurrent_groups = analysis.get("concurrent_groups", [])

            # Initialize results container
            results = {}

            # Process each concurrent group sequentially
            for group in concurrent_groups:
                # Prepare concurrent tasks for current group
                tasks = []
                for agent_name in group:
                    # Validate agent availability and requirement
                    if agent_name in required_agents and agent_name in self.agents:
                        tasks.append(self.agents[agent_name](state))

                # Execute group tasks concurrently if any exist
                if tasks:
                    # Gather results from concurrent execution
                    group_results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process successful results only
                    for agent_name, result in zip(group, group_results):
                        if not isinstance(result, Exception):
                            results[agent_name.lower()] = result

            # Implement fallback strategy if no results were obtained
            if not results and "PLANNER" in self.agents:
                planner_result = await self.agents["PLANNER"](state)
                results["planner"] = planner_result

            print("agent_outputs", results)

            # Return structured results
            return {
                "results": {
                    "agent_outputs": results
                }
            }

        except Exception as e:
            print(f"Execution error: {e}")
            # Emergency fallback with minimal response
            return {
                "results": {
                    "agent_outputs": {
                        "planner": {
                            "plan": "Emergency fallback plan: Please try again or contact support."
                        }
                    }
                }
            }
