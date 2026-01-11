"""Coordinator agent and profile analyzer for orchestrating multi-agent workflows."""

import json
from typing import Dict

from src.state.academic_state import AcademicState
from src.utils.context import analyze_context, parse_coordinator_response
from .prompts import COORDINATOR_PROMPT, PROFILE_ANALYZER_PROMPT


# Global LLM instance - will be set when creating the graph
llm = None


def set_llm(llm_instance):
    """Set the global LLM instance for coordinator functions."""
    global llm
    llm = llm_instance


async def coordinator_agent(state: AcademicState) -> Dict:
    """
    Primary coordinator agent that orchestrates multiple academic support agents using ReACT framework.

    This agent implements a sophisticated coordination strategy:
    1. Analyzes academic context and student needs
    2. Uses ReACT framework for structured decision making
    3. Coordinates parallel agent execution
    4. Handles fallback scenarios

    Args:
        state (AcademicState): Current academic state including messages and context

    Returns:
        Dict: Coordination analysis including required agents, priorities, and execution groups
    """
    try:
        context = await analyze_context(state)
        query = state["messages"][-1].content

        # Build conversation history summary for context
        history_summary = []
        for msg in state["messages"][:-1]:  # Exclude current message
            if hasattr(msg, 'content'):
                role = "User" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                # Truncate long messages
                content = msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
                history_summary.append(f"{role}: {content}")

        history_text = "\n".join(history_summary[-6:]) if history_summary else "No previous conversation"

        response = await llm.agenerate([
            {"role": "system", "content": COORDINATOR_PROMPT.format(
                request=query,
                context=json.dumps(context, indent=2),
                history=history_text
            )}
        ])

        analysis = parse_coordinator_response(response)
        return {
            "results": {
                "coordinator_analysis": {
                    "required_agents": analysis.get("required_agents", ["PLANNER"]),
                    "priority": analysis.get("priority", {"PLANNER": 1}),
                    "concurrent_groups": analysis.get("concurrent_groups", [["PLANNER"]]),
                    "reasoning": response
                }
            }
        }

    except Exception as e:
        print(f"Coordinator error: {e}")
        return {
            "results": {
                "coordinator_analysis": {
                    "required_agents": ["PLANNER"],
                    "priority": {"PLANNER": 1},
                    "concurrent_groups": [["PLANNER"]],
                    "reasoning": "Error in coordination. Falling back to planner."
                }
            }
        }


async def profile_analyzer(state: AcademicState) -> Dict:
    """
    Analyzes student profile data to extract and interpret learning preferences using ReACT framework.

    This agent specializes in:
    1. Deep analysis of student learning profiles
    2. Extraction of learning preferences and patterns
    3. Interpretation of academic history and tendencies
    4. Generation of personalized learning insights

    Args:
        state (AcademicState): Current academic state containing student profile data

    Returns:
        Dict: Structured analysis results including learning preferences and recommendations
    """
    profile = state["profile"]

    messages = [
        {"role": "system", "content": PROFILE_ANALYZER_PROMPT},
        {"role": "user", "content": json.dumps(profile)}
    ]

    response = await llm.agenerate(messages)

    return {
        "results": {
            "profile_analysis": {
                "analysis": response
            }
        }
    }
