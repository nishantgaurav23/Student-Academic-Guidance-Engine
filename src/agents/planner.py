"""Planner Agent for scheduling and time management."""

import json
from typing import Dict
from datetime import datetime, timezone, timedelta

from langgraph.graph import StateGraph

from src.state.academic_state import AcademicState
from .base import ReActAgent


class PlannerAgent(ReActAgent):
    """Planner agent with subgraph workflow for scheduling and time management."""

    def __init__(self, llm):
        """Initialize the Planner agent with LLM and example templates."""
        super().__init__(llm)
        self.llm = llm
        self.few_shot_examples = self._initialize_fewshots()
        self.workflow = self.create_subgraph()

    def _initialize_fewshots(self):
        """
        Define example scenarios to help the AI understand how to handle different situations.
        Each example shows:
        - Input: The student's request
        - Thought: The analysis process
        - Action: What needs to be done
        - Observation: What was found
        - Plan: The detailed solution
        """
        return [
            {
                "input": "Help with exam prep while managing ADHD and football",
                "thought": "Need to check calendar conflicts and energy patterns",
                "action": "search_calendar",
                "observation": "Football match at 6PM, exam tomorrow 9AM",
                "plan": """ADHD-OPTIMIZED SCHEDULE:
                    PRE-FOOTBALL (2PM-5PM):
                    - 3x20min study sprints
                    - Movement breaks
                    - Quick rewards after each sprint

                    FOOTBALL MATCH (6PM-8PM):
                    - Use as dopamine reset
                    - Formula review during breaks

                    POST-MATCH (9PM-12AM):
                    - Environment: Café noise
                    - 15/5 study/break cycles
                    - Location changes hourly

                    EMERGENCY PROTOCOLS:
                    - Focus lost → jumping jacks
                    - Overwhelmed → room change
                    - Brain fog → cold shower"""
            },
            {
                "input": "Struggling with multiple deadlines",
                "thought": "Check task priorities and performance issues",
                "action": "analyze_tasks",
                "observation": "3 assignments due, lowest grade in Calculus",
                "plan": """PRIORITY SCHEDULE:
                    HIGH-FOCUS SLOTS:
                    - Morning: Calculus practice
                    - Post-workout: Assignments
                    - Night: Quick reviews

                    ADHD MANAGEMENT:
                    - Task timer challenges
                    - Reward system per completion
                    - Study buddy accountability"""
            }
        ]

    def create_subgraph(self) -> StateGraph:
        """
        Create a workflow graph that defines how the planner processes requests:
        1. First analyzes calendar (calendar_analyzer)
        2. Then analyzes tasks (task_analyzer)
        3. Finally generates a plan (plan_generator)
        """
        subgraph = StateGraph(AcademicState)

        subgraph.add_node("calendar_analyzer", self.calendar_analyzer)
        subgraph.add_node("task_analyzer", self.task_analyzer)
        subgraph.add_node("plan_generator", self.plan_generator)

        subgraph.add_edge("calendar_analyzer", "task_analyzer")
        subgraph.add_edge("task_analyzer", "plan_generator")

        subgraph.set_entry_point("calendar_analyzer")

        return subgraph.compile()

    async def calendar_analyzer(self, state: AcademicState) -> Dict:
        """
        Analyze the student's calendar to find:
        - Available study times
        - Potential scheduling conflicts
        - Energy patterns throughout the day
        """
        events = state["calendar"].get("events", [])
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=7)

        filtered_events = [
            event for event in events
            if now <= datetime.fromisoformat(event["start"]["dateTime"]) <= future
        ]

        prompt = """Analyze calendar events and identify:
        Events: {events}

        Focus on:
        - Available time blocks
        - Energy impact of activities
        - Potential conflicts
        - Recovery periods
        - Study opportunity windows
        - Activity patterns
        - Schedule optimization
        """

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(filtered_events)}
        ]

        response = await self.llm.agenerate(messages)

        return {
            "results": {
                "calendar_analysis": {
                    "analysis": response
                }
            }
        }

    async def task_analyzer(self, state: AcademicState) -> Dict:
        """
        Analyze tasks to determine:
        - Priority order
        - Time needed for each task
        - Best approach for completion
        """
        tasks = state["tasks"].get("tasks", [])

        prompt = """Analyze tasks and create priority structure:
        Tasks: {tasks}

        Consider:
        - Urgency levels
        - Task complexity
        - Energy requirements
        - Dependencies
        - Required focus levels
        - Time estimations
        - Learning objectives
        - Success criteria
        """

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(tasks)}
        ]

        response = await self.llm.agenerate(messages)

        return {
            "results": {
                "task_analysis": {
                    "analysis": response
                }
            }
        }

    async def plan_generator(self, state: AcademicState) -> Dict:
        """
        Create a comprehensive study plan by combining:
        - Profile analysis (student's learning style)
        - Calendar analysis (available time)
        - Task analysis (what needs to be done)
        - Conversation history (previous context)
        """
        profile_analysis = state["results"]["profile_analysis"]
        calendar_analysis = state["results"]["calendar_analysis"]
        task_analysis = state["results"]["task_analysis"]

        # Build conversation context
        conversation_context = []
        for msg in state["messages"][:-1]:
            if hasattr(msg, 'content'):
                role = "User" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                content = msg.content[:400] + "..." if len(msg.content) > 400 else msg.content
                conversation_context.append(f"{role}: {content}")

        history_text = "\n".join(conversation_context[-4:]) if conversation_context else "This is the start of the conversation."

        prompt = f"""AI Planning Assistant: Create focused study plan using ReACT framework.

          INPUT CONTEXT:
          - Profile Analysis: {profile_analysis}
          - Calendar Analysis: {calendar_analysis}
          - Task Analysis: {task_analysis}

          CONVERSATION HISTORY:
          {history_text}

          EXAMPLES:
          {json.dumps(self.few_shot_examples, indent=2)}

          INSTRUCTIONS:
          1. Follow ReACT pattern:
            Thought: Analyze situation and needs
            Action: Consider all analyses
            Observation: Synthesize findings
            Plan: Create structured plan

          2. Address:
            - ADHD management strategies
            - Energy level optimization
            - Task chunking methods
            - Focus period scheduling
            - Environment switching tactics
            - Recovery period planning
            - Social/sport activity balance

          3. Include:
            - Emergency protocols
            - Backup strategies
            - Quick wins
            - Reward system
            - Progress tracking
            - Adjustment triggers

          4. If this is a follow-up question, reference and build upon the previous conversation context.

          Pls act as an intelligent tool to help the students reach their goals or overcome struggles and answer with informal words.

          FORMAT:
          Thought: [reasoning and situation analysis]
          Action: [synthesis approach]
          Observation: [key findings]
          Plan: [actionable steps and structural schedule]
          """

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": state["messages"][-1].content}
        ]

        response = await self.llm.agenerate(messages, temperature=0.5)

        return {
            "results": {
                "final_plan": {
                    "plan": response
                }
            }
        }

    async def __call__(self, state: AcademicState) -> Dict:
        """
        Main execution method that runs the entire planning workflow.
        """
        try:
            final_state = await self.workflow.ainvoke(state)
            final_plan = final_state["results"].get("final_plan", {})
            return {"plan": final_plan.get("plan", "No plan generated.")}
        except Exception as e:
            return {"plan": f"Error generating plan: {str(e)}"}
