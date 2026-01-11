"""Context analysis utilities for coordinator decision-making."""

import json
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from src.state.academic_state import AcademicState


async def analyze_context(state: "AcademicState") -> Dict:
    """
    Analyzes the academic state context to inform coordinator decision-making.

    This function performs comprehensive context analysis by:
    1. Extracting student profile information
    2. Analyzing calendar and task loads
    3. Identifying relevant course context from the latest message
    4. Gathering learning preferences and study patterns

    Args:
        state (AcademicState): Current academic state including profile, calendar, and tasks

    Returns:
        Dict: Structured analysis of the student's context for decision making

    Implementation Notes:
        - Extracts information hierarchically using nested get() operations for safety
        - Identifies current course context from the latest message content
        - Provides default values for missing information to ensure stability
    """
    # Extract main data components with safe navigation
    profile = state.get("profile", {})
    calendar = state.get("calendar", {})
    tasks = state.get("tasks", {})

    # Extract course information and match with current request
    courses = profile.get("academic_info", {}).get("current_courses", [])
    current_course = None
    request = state["messages"][-1].content.lower()

    # Identify relevant course from request content
    for course in courses:
        if course["name"].lower() in request:
            current_course = course
            break

    # Construct comprehensive context analysis
    return {
        "student": {
            "major": profile.get("personal_info", {}).get("major", "Unknown"),
            "year": profile.get("personal_info", {}).get("academic_year"),
            "learning_style": profile.get("learning_preferences", {}).get("learning_style", {}),
        },
        "course": current_course,
        "upcoming_events": len(calendar.get("events", [])),
        "active_tasks": len(tasks.get("tasks", [])),
        "study_patterns": profile.get("learning_preferences", {}).get("study_patterns", {})
    }


def parse_coordinator_response(response: str) -> Dict:
    """
    Parses LLM coordinator response into structured analysis for agent execution.

    This function implements a robust parsing strategy:
    1. Starts with safe default configuration
    2. Analyzes ReACT patterns in the response
    3. Adjusts agent requirements and priorities based on content
    4. Organizes concurrent execution groups

    Args:
        response (str): Raw LLM response text

    Returns:
        Dict: Structured analysis containing:
            - required_agents: List of agents needed
            - priority: Priority levels for each agent
            - concurrent_groups: Groups of agents that can run together
            - reasoning: Extracted reasoning for decisions
    """
    try:
        # Initialize with safe default configuration
        analysis = {
            "required_agents": ["PLANNER"],
            "priority": {"PLANNER": 1},
            "concurrent_groups": [["PLANNER"]],
            "reasoning": response
        }

        # Parse ReACT patterns for advanced coordination
        if "Thought:" in response and "Decision:" in response:
            # Check for NOTEWRITER requirements
            if "NOTEWRITER" in response or "note" in response.lower():
                analysis["required_agents"].append("NOTEWRITER")
                analysis["priority"]["NOTEWRITER"] = 2
                analysis["concurrent_groups"] = [["PLANNER", "NOTEWRITER"]]

            # Check for ADVISOR requirements
            if "ADVISOR" in response or "guidance" in response.lower():
                analysis["required_agents"].append("ADVISOR")
                analysis["priority"]["ADVISOR"] = 3

        return analysis

    except Exception as e:
        print(f"Parse error: {str(e)}")
        return {
            "required_agents": ["PLANNER"],
            "priority": {"PLANNER": 1},
            "concurrent_groups": [["PLANNER"]],
            "reasoning": "Fallback due to parse error"
        }
