"""Advisor Agent for personalized academic guidance."""

import json
from typing import Dict

from langgraph.graph import StateGraph, END, START

from src.state.academic_state import AcademicState
from .base import ReActAgent


class AdvisorAgent(ReActAgent):
    """Academic advisor agent with subgraph workflow for personalized guidance.

    This agent specializes in analyzing student situations and providing
    tailored academic advice considering learning styles and time constraints.
    """

    def __init__(self, llm):
        """Initialize the Advisor agent with an LLM backend and example templates.

        Args:
            llm: Language model instance for text generation
        """
        super().__init__(llm)
        self.llm = llm

        self.few_shot_examples = [
            {
                "request": "Managing multiple deadlines with limited time",
                "profile": {
                    "learning_style": "visual",
                    "workload": "heavy",
                    "time_constraints": ["2 hackathons", "project", "exam"]
                },
                "advice": """PRIORITY-BASED SCHEDULE:

                1. IMMEDIATE ACTIONS
                   • Create visual timeline of all deadlines
                   • Break each task into 45-min chunks
                   • Schedule high-focus work in mornings

                2. WORKLOAD MANAGEMENT
                   • Hackathons: Form team early, set clear roles
                   • Project: Daily 2-hour focused sessions
                   • Exam: Interleaved practice with breaks

                3. ENERGY OPTIMIZATION
                   • Use Pomodoro (25/5) for intensive tasks
                   • Physical activity between study blocks
                   • Regular progress tracking

                4. EMERGENCY PROTOCOLS
                   • If overwhelmed: Take 10min reset break
                   • If stuck: Switch tasks or environments
                   • If tired: Quick power nap, then review"""
            }
        ]
        self.workflow = self.create_subgraph()

    def create_subgraph(self) -> StateGraph:
        """Creates Advisor's internal workflow as a state machine.

        The workflow consists of two main stages:
        1. Situation analysis - Understanding student needs
        2. Guidance generation - Creating personalized advice

        Returns:
            StateGraph: Compiled workflow graph
        """
        subgraph = StateGraph(AcademicState)

        subgraph.add_node("advisor_analyze", self.analyze_situation)
        subgraph.add_node("advisor_generate", self.generate_guidance)

        subgraph.add_edge(START, "advisor_analyze")
        subgraph.add_edge("advisor_analyze", "advisor_generate")
        subgraph.add_edge("advisor_generate", END)

        return subgraph.compile()

    async def analyze_situation(self, state: AcademicState) -> Dict:
        """Analyzes student's current academic situation and needs.

        Evaluates:
        - Student profile and preferences
        - Current challenges and constraints
        - Learning style compatibility
        - Time and stress management needs

        Args:
            state: Current academic state with student profile and request

        Returns:
            Updated state with situation analysis results
        """
        profile = state["profile"]
        learning_prefs = profile.get("learning_preferences", {})

        prompt = f"""Analyze student situation and determine guidance approach:

        CONTEXT:
        - Profile: {json.dumps(profile, indent=2)}
        - Learning Preferences: {json.dumps(learning_prefs, indent=2)}
        - Request: {state['messages'][-1].content}

        ANALYZE:
        1. Current challenges
        2. Learning style compatibility
        3. Time management needs
        4. Stress management requirements
        """

        response = await self.llm.agenerate([
            {"role": "system", "content": prompt}
        ])

        return {
            "results": {
                "situation_analysis": {
                    "analysis": response
                }
            }
        }

    async def generate_guidance(self, state: AcademicState) -> Dict:
        """Generates personalized academic guidance based on situation analysis.

        Creates structured advice focusing on:
        - Immediate actionable steps
        - Schedule optimization
        - Energy and resource management
        - Support strategies
        - Contingency planning

        Args:
            state: Current academic state with situation analysis

        Returns:
            Updated state with generated guidance
        """
        analysis = state["results"].get("situation_analysis", "")

        # Build conversation context
        conversation_context = []
        for msg in state["messages"][:-1]:
            if hasattr(msg, 'content'):
                role = "User" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                content = msg.content[:400] + "..." if len(msg.content) > 400 else msg.content
                conversation_context.append(f"{role}: {content}")

        history_text = "\n".join(conversation_context[-4:]) if conversation_context else "This is the start of the conversation."

        prompt = f"""Generate personalized academic guidance based on analysis:

        ANALYSIS: {analysis}
        REQUEST: {state['messages'][-1].content}

        CONVERSATION HISTORY:
        {history_text}

        EXAMPLES: {json.dumps(self.few_shot_examples, indent=2)}

        If this is a follow-up question, reference and build upon the previous conversation context.

        FORMAT:
        1. Immediate Action Steps
        2. Schedule Optimization
        3. Energy Management
        4. Support Strategies
        5. Emergency Protocols
        """

        response = await self.llm.agenerate([
            {"role": "system", "content": prompt}
        ])

        return {
            "results": {
                "guidance": {
                    "advice": response
                }
            }
        }

    async def __call__(self, state: AcademicState) -> Dict:
        """Main execution method for the Advisor agent.

        Executes the complete advisory workflow:
        1. Analyzes student situation
        2. Generates personalized guidance
        3. Returns formatted results

        Args:
            state: Initial academic state

        Returns:
            Dict containing guidance or error message
        """
        try:
            final_state = await self.workflow.ainvoke(state)
            guidance = final_state["results"].get("guidance", {})
            return {"advice": guidance.get("advice", "No guidance generated.")}
        except Exception as e:
            return {"advice": f"Error generating guidance: {str(e)}"}
