"""NoteWriter Agent for generating personalized study materials."""

import json
from typing import Dict

from langgraph.graph import StateGraph, END, START

from src.state.academic_state import AcademicState
from .base import ReActAgent


class NoteWriterAgent(ReActAgent):
    """NoteWriter agent with its own subgraph workflow for note generation.

    This agent specializes in creating personalized study materials by analyzing
    learning styles and generating structured notes.
    """

    def __init__(self, llm):
        """Initialize the NoteWriter agent with an LLM backend and example templates.

        Args:
            llm: Language model instance for text generation
        """
        super().__init__(llm)
        self.llm = llm
        self.few_shot_examples = [
            {
                "input": "Need to cram Calculus III for tomorrow",
                "template": "Quick Review",
                "notes": """CALCULUS III ESSENTIALS:

                1. CORE CONCEPTS (80/20 Rule):
                   • Multiple Integrals → volume/area
                   • Vector Calculus → flow/force/rotation
                   • KEY FORMULAS:
                     - Triple integrals in cylindrical/spherical coords
                     - Curl, divergence, gradient relationships

                2. COMMON EXAM PATTERNS:
                   • Find critical points
                   • Calculate flux/work
                   • Optimize with constraints

                3. QUICKSTART GUIDE:
                   • Always draw 3D diagrams
                   • Check units match
                   • Use symmetry to simplify

                4. EMERGENCY TIPS:
                   • If stuck, try converting coordinates
                   • Check boundary conditions
                   • Look for special patterns"""
            }
        ]
        self.workflow = self.create_subgraph()

    def create_subgraph(self) -> StateGraph:
        """Creates NoteWriter's internal workflow as a state machine.

        The workflow consists of two main steps:
        1. Analyze learning style and content requirements
        2. Generate personalized notes

        Returns:
            StateGraph: Compiled workflow graph
        """
        subgraph = StateGraph(AcademicState)

        subgraph.add_node("notewriter_analyze", self.analyze_learning_style)
        subgraph.add_node("notewriter_generate", self.generate_notes)

        subgraph.add_edge(START, "notewriter_analyze")
        subgraph.add_edge("notewriter_analyze", "notewriter_generate")
        subgraph.add_edge("notewriter_generate", END)

        return subgraph.compile()

    async def analyze_learning_style(self, state: AcademicState) -> Dict:
        """Analyzes student profile and request to determine optimal note structure.

        Uses the LLM to analyze:
        - Student's learning style preferences
        - Specific content request
        - Time constraints and requirements

        Args:
            state: Current academic state containing student profile and messages

        Returns:
            Updated state with learning analysis results
        """
        profile = state["profile"]
        learning_style = profile["learning_preferences"]["learning_style"]

        prompt = f"""Analyze content requirements and determine optimal note structure:

        STUDENT PROFILE:
        - Learning Style: {json.dumps(learning_style, indent=2)}
        - Request: {state['messages'][-1].content}

        FORMAT:
        1. Key Topics (80/20 principle)
        2. Learning Style Adaptations
        3. Time Management Strategy
        4. Quick Reference Format

        FOCUS ON:
        - Essential concepts that give maximum understanding
        - Visual and interactive elements
        - Time-optimized study methods
        """

        response = await self.llm.agenerate([
            {"role": "system", "content": prompt}
        ])

        return {
            "results": {
                "learning_analysis": {
                    "analysis": response
                }
            }
        }

    async def generate_notes(self, state: AcademicState) -> Dict:
        """Generates personalized study notes based on the learning analysis.

        Uses the LLM to create structured notes that are:
        - Adapted to the student's learning style
        - Focused on essential concepts (80/20 principle)
        - Time-optimized for the study period

        Args:
            state: Current academic state with learning analysis

        Returns:
            Updated state with generated notes
        """
        analysis = state["results"].get("learning_analysis", "")
        learning_style = state["profile"]["learning_preferences"]["learning_style"]

        # Build conversation context
        conversation_context = []
        for msg in state["messages"][:-1]:
            if hasattr(msg, 'content'):
                role = "User" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                content = msg.content[:400] + "..." if len(msg.content) > 400 else msg.content
                conversation_context.append(f"{role}: {content}")

        history_text = "\n".join(conversation_context[-4:]) if conversation_context else "This is the start of the conversation."

        prompt = f"""Create concise, high-impact study materials based on analysis:

        ANALYSIS: {analysis}
        LEARNING STYLE: {json.dumps(learning_style, indent=2)}
        REQUEST: {state['messages'][-1].content}

        CONVERSATION HISTORY:
        {history_text}

        EXAMPLES:
        {json.dumps(self.few_shot_examples, indent=2)}

        If this is a follow-up question, reference and build upon the previous conversation context.

        FORMAT:
        **THREE-WEEK INTENSIVE STUDY PLANNER**

        [Generate structured notes with:]
        1. Weekly breakdown
        2. Daily focus areas
        3. Core concepts
        4. Emergency tips
        """

        response = await self.llm.agenerate([
            {"role": "system", "content": prompt}
        ])

        return {
            "results": {
                "generated_notes": {
                    "notes": response
                }
            }
        }

    async def __call__(self, state: AcademicState) -> Dict:
        """Main execution method for the NoteWriter agent.

        Executes the complete workflow:
        1. Analyzes learning requirements
        2. Generates personalized notes
        3. Cleans and returns the results

        Args:
            state: Initial academic state

        Returns:
            Dict containing generated notes or error message
        """
        try:
            final_state = await self.workflow.ainvoke(state)
            generated_notes = final_state["results"].get("generated_notes", {})
            return {"notes": generated_notes.get("notes", "No notes generated.")}
        except Exception as e:
            return {"notes": f"Error generating notes: {str(e)}"}
