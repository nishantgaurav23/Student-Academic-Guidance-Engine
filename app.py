"""Streamlit app for SAGE: Student Academic Guidance Engine."""

import os
import json
import asyncio

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.llm import GeminiLLM
from src.utils.data_manager import DataManager
from src.graph import create_agents_graph


# Page configuration
st.set_page_config(
    page_title="SAGE - Academic Assistant",
    page_icon="🎓",
    layout="wide"
)


def load_data():
    """Load data files."""
    with open("data/sample_profile.json", "r") as f:
        profile_data = f.read()
    with open("data/sample_calendar.json", "r") as f:
        calendar_data = f.read()
    with open("data/sample_tasks.json", "r") as f:
        task_data = f.read()
    return profile_data, calendar_data, task_data


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "profile_data" not in st.session_state:
        profile, calendar, tasks = load_data()
        st.session_state.profile_data = profile
        st.session_state.calendar_data = calendar
        st.session_state.task_data = tasks


def build_conversation_history(messages: list) -> list:
    """Convert session messages to LangChain message format."""
    history = []
    for msg in messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            # Extract text summary from agent results for context
            outputs = msg.get("results", {}).get("outputs", {})
            summary_parts = []
            for agent_name, output in outputs.items():
                if isinstance(output, dict):
                    for key, value in output.items():
                        if isinstance(value, str) and value:
                            # Truncate long responses for context
                            summary_parts.append(f"[{agent_name}]: {value[:500]}...")
                elif isinstance(output, str):
                    summary_parts.append(f"[{agent_name}]: {output[:500]}...")
            if summary_parts:
                history.append(AIMessage(content="\n".join(summary_parts)))
    return history


async def run_agent_workflow(user_input: str, api_key: str, conversation_history: list):
    """Run the multi-agent workflow with conversation context."""
    # Initialize LLM
    llm = GeminiLLM(api_key)

    # Initialize data manager
    dm = DataManager()
    dm.load_data(
        st.session_state.profile_data,
        st.session_state.calendar_data,
        st.session_state.task_data
    )

    # Build messages with conversation history
    messages = conversation_history + [HumanMessage(content=user_input)]

    # Construct initial state
    state = {
        "messages": messages,
        "profile": dm.get_student_profile("student_123"),
        "calendar": {"events": dm.get_upcoming_events()},
        "tasks": {"tasks": dm.get_active_tasks()},
        "results": {}
    }

    # Create and run workflow
    graph = create_agents_graph(llm)

    results = {
        "coordinator": None,
        "agents": [],
        "outputs": {}
    }

    async for step in graph.astream(state):
        # Capture coordinator analysis
        if "results" in step and "coordinator_analysis" in step.get("results", {}):
            results["coordinator"] = step["results"]["coordinator_analysis"]
            results["agents"] = step["results"]["coordinator_analysis"].get("required_agents", [])

        # Capture agent outputs from execute step
        if "execute" in step:
            exec_results = step["execute"].get("results", {})
            if "agent_outputs" in exec_results:
                results["outputs"] = exec_results["agent_outputs"]

    return results


def display_results(results: dict):
    """Display agent results."""
    if not results:
        st.error("No results generated.")
        return

    # Show which agents were activated
    if results.get("agents"):
        st.info(f"**Agents activated:** {', '.join(results['agents'])}")

    # Display outputs from each agent
    outputs = results.get("outputs", {})

    if not outputs:
        st.warning("No agent outputs available.")
        return

    for agent_name, agent_output in outputs.items():
        st.markdown(f"### {agent_name.upper()}")

        if isinstance(agent_output, dict):
            # Handle nested output structure
            for key, value in agent_output.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if subvalue and isinstance(subvalue, str):
                            st.markdown(subvalue)
                elif isinstance(value, str) and value:
                    st.markdown(value)
        elif isinstance(agent_output, str):
            st.markdown(agent_output)

        st.markdown("---")


def main():
    """Main Streamlit app."""
    init_session_state()

    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY", "")

    # Header
    st.title("🎓 SAGE")
    st.subheader("Student Academic Guidance Engine")
    st.markdown("*Powered by Google Gemini*")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("💡 Try These")
        examples = [
            "Help me prepare for my Calculus exam",
            "Create a study schedule for this week",
            "I'm struggling with deadlines",
            "Generate study notes for Data Structures"
        ]
        for example in examples:
            if st.button(example, key=example, use_container_width=True):
                st.session_state.pending_prompt = example

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Main chat area
    st.header("💬 Chat with SAGE")

    # Check API key
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY not set. Please set it in your environment.")
        st.code("export GOOGLE_API_KEY=your_api_key_here")
        return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                display_results(message.get("results", {}))

    # Handle pending prompt from sidebar
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt
    else:
        prompt = st.chat_input("Enter your academic request...")

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process with agents
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    # Build conversation history from previous messages
                    history = build_conversation_history(st.session_state.messages[:-1])
                    results = asyncio.run(run_agent_workflow(prompt, api_key, history))
                    display_results(results)
                    st.session_state.messages.append({"role": "assistant", "results": results})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
