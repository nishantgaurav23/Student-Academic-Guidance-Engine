"""Academic State management for the multi-agent system."""

from typing import Annotated, List, Dict, Any, TypedDict
from operator import add

from langchain_core.messages import BaseMessage

from src.utils.reducers import dict_reducer


class AcademicState(TypedDict):
    """Master state container for the academic assistance system.

    Attributes:
        messages: Conversation history with the student
        profile: Student information and preferences
        calendar: Scheduled events and calendar data
        tasks: To-do items and assignments
        results: Operation outputs from agents
    """
    messages: Annotated[List[BaseMessage], add]
    profile: Annotated[Dict, dict_reducer]
    calendar: Annotated[Dict, dict_reducer]
    tasks: Annotated[Dict, dict_reducer]
    results: Annotated[Dict[str, Any], dict_reducer]
