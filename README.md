# SAGE - Student Academic Guidance Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.1+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-API-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**An intelligent multi-agent system for personalized academic assistance**

[Features](#features) | [Installation](#installation) | [Usage](#usage) | [Architecture](#architecture) | [Contributing](#contributing)

</div>

---

## Overview

SAGE (Student Academic Guidance Engine) is a sophisticated multi-agent AI system built with LangGraph that provides personalized academic support to students. It leverages Google's Gemini AI to coordinate multiple specialized agents that work together to help students with scheduling, study materials, and academic guidance.

### Key Highlights

- **Multi-Agent Architecture**: Three specialized agents (Planner, NoteWriter, Advisor) coordinated by an intelligent orchestrator
- **Conversation Memory**: Maintains context across conversations for coherent, follow-up interactions
- **Personalized Responses**: Adapts to student learning styles, preferences, and schedules
- **ReACT Framework**: Uses Reasoning and Acting patterns for structured decision-making
- **Parallel Execution**: Efficiently runs compatible agents concurrently

---

## Features

### Specialized Agents

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| **Coordinator** | Orchestrates workflow | Analyzes requests, routes to appropriate agents, manages parallel execution |
| **Planner** | Schedule management | Creates study schedules, analyzes calendars, manages time blocks, ADHD-friendly planning |
| **NoteWriter** | Study materials | Generates personalized notes, adapts to learning styles, creates summaries |
| **Advisor** | Academic guidance | Provides personalized advice, stress management, deadline strategies |

### Core Capabilities

- **Intelligent Routing**: Automatically determines which agents to activate based on user requests
- **Context-Aware**: Considers student profile, calendar, tasks, and conversation history
- **Adaptive Learning**: Tailors responses to visual, auditory, or kinesthetic learning styles
- **Emergency Protocols**: Includes backup strategies and quick-win suggestions

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Google API Key (for Gemini)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Academic-Task-Learning-Agent-LangGraph.git
   cd Academic-Task-Learning-Agent-LangGraph
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env and add your Google API key
   ```

   Get your API key from: https://aistudio.google.com/apikey

---

## Usage

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables and run
export $(grep -v '^#' config/.env | xargs)
streamlit run app.py
```

The app will be available at `http://localhost:8502`

### Example Prompts

| Category | Example Prompts |
|----------|-----------------|
| **Planning** | "Create a study schedule for this week" |
| **Exam Prep** | "Help me prepare for my Calculus exam" |
| **Deadlines** | "I'm struggling with multiple deadlines" |
| **Notes** | "Generate study notes for Data Structures" |
| **Follow-up** | "Can you focus more on mornings?" |

### Conversation Flow

1. Enter your academic request in the chat
2. SAGE analyzes your request and activates relevant agents
3. View personalized responses from each agent
4. Ask follow-up questions - SAGE remembers context
5. Use "Clear Chat" to start a new conversation

---

## Architecture

SAGE uses a sophisticated multi-agent architecture built on LangGraph. For detailed architecture documentation, see [ARCHITECTURE.md](./ARCHITECTURE.md).

### High-Level Flow

```
User Request
     │
     ▼
┌─────────────┐
│ Coordinator │ ─── Analyzes request & routes
└─────────────┘
     │
     ▼
┌─────────────────┐
│Profile Analyzer │ ─── Extracts learning preferences
└─────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│     Parallel Agent Execution        │
│  ┌─────────┐ ┌──────────┐ ┌───────┐│
│  │ Planner │ │NoteWriter│ │Advisor││
│  └─────────┘ └──────────┘ └───────┘│
└─────────────────────────────────────┘
     │
     ▼
┌──────────┐
│ Executor │ ─── Consolidates results
└──────────┘
     │
     ▼
  Response
```

---

## Project Structure

```
Academic-Task-Learning-Agent-LangGraph/
├── app.py                    # Streamlit web application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── ARCHITECTURE.md           # Detailed architecture documentation
├── .gitignore               # Git ignore rules
│
├── config/
│   ├── .env.example         # Environment variables template
│   └── .env                 # Your API keys (not in git)
│
├── data/
│   ├── sample_profile.json  # Student profile data
│   ├── sample_calendar.json # Calendar events
│   └── sample_tasks.json    # Task/assignment data
│
└── src/
    ├── __init__.py
    ├── graph.py             # LangGraph workflow definition
    ├── main.py              # CLI entry point
    │
    ├── agents/
    │   ├── __init__.py
    │   ├── base.py          # Base agent class (ReACT)
    │   ├── coordinator.py   # Orchestration agent
    │   ├── planner.py       # Schedule planning agent
    │   ├── notewriter.py    # Note generation agent
    │   ├── advisor.py       # Academic guidance agent
    │   └── prompts.py       # Prompt templates
    │
    ├── executor/
    │   ├── __init__.py
    │   └── agent_executor.py # Parallel execution handler
    │
    ├── llm/
    │   ├── __init__.py
    │   ├── config.py        # LLM configuration
    │   └── gemini_llm.py    # Gemini API wrapper
    │
    ├── models/
    │   ├── __init__.py
    │   └── agent_models.py  # Pydantic models
    │
    ├── state/
    │   ├── __init__.py
    │   └── academic_state.py # State management
    │
    └── utils/
        ├── __init__.py
        ├── context.py       # Context analysis
        ├── data_manager.py  # Data loading/management
        └── reducers.py      # State reducers
```

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |

### LLM Configuration

Edit `src/llm/config.py` to customize:
- Model selection (default: `gemini-1.5-flash`)
- Temperature settings
- Max output tokens

---

## Technologies

| Technology | Purpose |
|------------|---------|
| **LangGraph** | Multi-agent orchestration and state management |
| **LangChain** | LLM integration and message handling |
| **Google Gemini** | Large language model backend |
| **Streamlit** | Web interface |
| **Pydantic** | Data validation and models |

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) by LangChain
- Powered by [Google Gemini](https://ai.google.dev/)
- UI framework: [Streamlit](https://streamlit.io/)

---

<div align="center">

**Made with intelligence for students**

</div>
