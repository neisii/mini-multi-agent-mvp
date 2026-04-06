# Mini Multi-Agent MVP

A LangGraph-based multi-agent system that automatically generates a REST API, writes tests, and iteratively fixes code until all tests pass.

## How It Works

```
User Task → Coder Agent → Tester Agent → PASS? → Done
                ↑               |
                └───── FAIL ────┘  (up to 5 iterations)
```

| Agent | Role |
|-------|------|
| **Coder Agent** | Generates or fixes FastAPI source code using OpenAI |
| **Tester Agent** | Generates pytest tests, runs them, reports SUCCESS / FAIL |
| **Orchestrator** | Routes between agents; stops on success, max iterations, or repeated error |

## Prerequisites

- Python 3.10+
- OpenAI API key

## Setup

```bash
# 1. Clone
git clone https://github.com/neisii/mini-multi-agent-mvp.git
cd mini-multi-agent-mvp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required. Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used by both agents |

## Run

```bash
python main.py
```

Generated files are written to `workspace/`:
- `workspace/app.py` — the generated FastAPI application
- `workspace/test_app.py` — the generated pytest test suite

## Loop Rules

- Maximum **5 iterations**
- Stops immediately when all tests **pass**
- Stops if the **same error repeats** twice in a row

## Project Structure

```
mini-multi-agent-mvp/
├── state.py                 # AgentState TypedDict
├── agents/
│   ├── coder_agent.py       # Code generation / repair
│   └── tester_agent.py      # Test generation + execution
├── graph/
│   └── workflow.py          # LangGraph StateGraph
├── workspace/               # Generated output (git-ignored)
├── main.py                  # Entry point
└── requirements.txt
```
