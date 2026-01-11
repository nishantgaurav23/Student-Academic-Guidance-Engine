"""Agents module for academic support system."""

from .base import ReActAgent
from .planner import PlannerAgent
from .notewriter import NoteWriterAgent
from .advisor import AdvisorAgent
from .coordinator import coordinator_agent, profile_analyzer, set_llm
from .prompts import COORDINATOR_PROMPT, PROFILE_ANALYZER_PROMPT

__all__ = [
    "ReActAgent",
    "PlannerAgent",
    "NoteWriterAgent",
    "AdvisorAgent",
    "coordinator_agent",
    "profile_analyzer",
    "set_llm",
    "COORDINATOR_PROMPT",
    "PROFILE_ANALYZER_PROMPT"
]
