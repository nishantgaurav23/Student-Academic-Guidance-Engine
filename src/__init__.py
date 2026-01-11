"""ATLAS: Academic Task Learning Agent System.

A multi-agent system for personalized academic support using LangGraph.
"""

from .llm import LLMConfig, GeminiLLM
from .state import AcademicState
from .graph import create_agents_graph

__version__ = "0.1.0"

__all__ = [
    "LLMConfig",
    "GeminiLLM",
    "AcademicState",
    "create_agents_graph"
]
