"""Main entry point for the ATLAS Academic Task Learning Agent System."""

import os
import re
import json
import asyncio
import traceback

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from langchain_core.messages import HumanMessage

from src.llm import GeminiLLM
from src.utils.data_manager import DataManager
from src.graph import create_agents_graph


async def run_all_system(profile_json: str, calendar_json: str, task_json: str):
    """Run the entire academic assistance system with improved output handling.

    This is the main entry point for the ATLAS (Academic Task Learning Agent System).
    It handles initialization, user interaction, workflow execution, and result presentation.

    Args:
        profile_json: JSON string containing student profile data
        calendar_json: JSON string containing calendar/schedule data
        task_json: JSON string containing academic tasks data

    Returns:
        Tuple[Dict, Dict]: Coordinator output and final state, or (None, None) on error
    """
    try:
        console = Console()

        console.print("\n[bold magenta]ATLAS: Academic Task Learning Agent System[/bold magenta]")
        console.print("[italic blue]Initializing academic support system...[/italic blue]\n")

        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            console.print("[bold red]Error: GOOGLE_API_KEY not found in environment[/bold red]")
            return None, None

        # Initialize core system components
        llm = GeminiLLM(api_key)

        # DataManager handles all data loading and access
        dm = DataManager()
        dm.load_data(profile_json, calendar_json, task_json)

        # Get user request
        console.print("[bold green]Please enter your academic request:[/bold green]")
        user_input = str(input())
        console.print(f"\n[dim italic]Processing request: {user_input}[/dim italic]\n")

        # Construct initial state object
        state = {
            "messages": [HumanMessage(content=user_input)],
            "profile": dm.get_student_profile("student_123"),
            "calendar": {"events": dm.get_upcoming_events()},
            "tasks": {"tasks": dm.get_active_tasks()},
            "results": {}
        }

        # Initialize workflow graph for agent orchestration
        graph = create_agents_graph(llm)

        console.print("[bold cyan]System initialized and processing request...[/bold cyan]\n")

        # Track important state transitions
        coordinator_output = None
        final_state = None

        # Process workflow with live status updates
        with console.status("[bold green]Processing...", spinner="dots") as status:
            async for step in graph.astream(state):
                if "coordinator_analysis" in step.get("results", {}):
                    coordinator_output = step
                    analysis = coordinator_output["results"]["coordinator_analysis"]

                    console.print("\n[bold cyan]Selected Agents:[/bold cyan]")
                    for agent in analysis.get("required_agents", []):
                        console.print(f"  - {agent}")

                if "execute" in step:
                    final_state = step

        # Display results
        if final_state:
            agent_outputs = final_state.get("execute", {}).get("results", {}).get("agent_outputs", {})

            for agent, output in agent_outputs.items():
                console.print(f"\n[bold cyan]{agent.upper()} Output:[/bold cyan]")

                if isinstance(output, dict):
                    for key, value in output.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subvalue and isinstance(subvalue, str):
                                    console.print(subvalue.strip())
                        elif value and isinstance(value, str):
                            console.print(value.strip())
                elif isinstance(output, str):
                    console.print(output.strip())

        console.print("\n[bold green]Task completed![/bold green]")
        return coordinator_output, final_state

    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]System error:[/bold red] {str(e)}")
        console.print("[yellow]Stack trace:[/yellow]")
        console.print(traceback.format_exc())
        return None, None


async def load_json_and_run(profile_path: str, calendar_path: str, task_path: str):
    """Load JSON files from paths and run the academic assistance system.

    Args:
        profile_path: Path to profile JSON file
        calendar_path: Path to calendar JSON file
        task_path: Path to task JSON file

    Returns:
        Tuple[Dict, Dict]: Coordinator output and final state, or (None, None) on error
    """
    console = Console()
    console.print("Academic Assistant Setup")
    console.print("-" * 50)

    try:
        # Load JSON files
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_json = f.read()
        with open(calendar_path, 'r', encoding='utf-8') as f:
            calendar_json = f.read()
        with open(task_path, 'r', encoding='utf-8') as f:
            task_json = f.read()

        console.print("\nFiles loaded successfully!")
        console.print("\nStarting academic assistance workflow...")

        return await run_all_system(profile_json, calendar_json, task_json)

    except FileNotFoundError as e:
        console.print(f"\n[bold red]Error: File not found - {e}[/bold red]")
        return None, None
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        console.print(traceback.format_exc())
        return None, None


def main():
    """Main function to run the ATLAS system."""
    import argparse

    parser = argparse.ArgumentParser(description="ATLAS: Academic Task Learning Agent System")
    parser.add_argument("--profile", required=True, help="Path to profile JSON file")
    parser.add_argument("--calendar", required=True, help="Path to calendar JSON file")
    parser.add_argument("--tasks", required=True, help="Path to tasks JSON file")

    args = parser.parse_args()

    asyncio.run(load_json_and_run(args.profile, args.calendar, args.tasks))


if __name__ == "__main__":
    main()
