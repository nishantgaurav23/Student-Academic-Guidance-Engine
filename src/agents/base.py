"""Base ReActAgent class for all specialized agents."""

from typing import List, Dict
from datetime import datetime, timezone

from src.state.academic_state import AcademicState


class ReActAgent:
    """
    Base class for ReACT-based agents implementing reasoning and action capabilities.

    Features:
    - Tool management for specific actions
    - Few-shot learning examples
    - Structured thought process
    - Action execution framework
    """

    def __init__(self, llm):
        """
        Initialize the ReActAgent with language model and available tools.

        Args:
            llm: Language model instance for agent operations
        """
        self.llm = llm
        self.few_shot_examples = []

        # Dictionary of available tools with their corresponding methods
        self.tools = {
            "search_calendar": self.search_calendar,
            "analyze_tasks": self.analyze_tasks,
            "check_learning_style": self.check_learning_style,
            "check_performance": self.check_performance
        }

    async def search_calendar(self, state: AcademicState) -> List[Dict]:
        """
        Search for upcoming calendar events.

        Args:
            state (AcademicState): Current academic state

        Returns:
            List[Dict]: List of upcoming calendar events
        """
        events = state["calendar"].get("events", [])
        now = datetime.now(timezone.utc)
        return [e for e in events if datetime.fromisoformat(e["start"]["dateTime"]) > now]

    async def analyze_tasks(self, state: AcademicState) -> List[Dict]:
        """
        Analyze academic tasks from the current state.

        Args:
            state (AcademicState): Current academic state

        Returns:
            List[Dict]: List of academic tasks
        """
        return state["tasks"].get("tasks", [])

    async def check_learning_style(self, state: AcademicState) -> AcademicState:
        """
        Retrieve student's learning style and study patterns.

        Args:
            state (AcademicState): Current academic state

        Returns:
            AcademicState: Updated state with learning style analysis
        """
        profile = state["profile"]

        learning_data = {
            "style": profile.get("learning_preferences", {}).get("learning_style", {}),
            "patterns": profile.get("learning_preferences", {}).get("study_patterns", {})
        }

        if "results" not in state:
            state["results"] = {}
        state["results"]["learning_analysis"] = learning_data

        return state

    async def check_performance(self, state: AcademicState) -> AcademicState:
        """
        Check current academic performance across courses.

        Args:
            state (AcademicState): Current academic state

        Returns:
            AcademicState: Updated state with performance analysis
        """
        profile = state["profile"]
        courses = profile.get("academic_info", {}).get("current_courses", [])

        if "results" not in state:
            state["results"] = {}
        state["results"]["performance_analysis"] = {"courses": courses}

        return state
