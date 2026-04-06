import os
from openai import OpenAI
from state import AgentState

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_SYSTEM_PROMPT = """You are a Coder Agent. Your job is to generate or fix executable Python code.

Rules:
- Output ONLY raw Python code — no markdown, no code fences, no explanations
- Code must be complete and immediately runnable
- Use FastAPI for the REST API
- Use an in-memory data store (no database required)
- All modifications must be based strictly on the provided failure log
"""

_INITIAL_TEMPLATE = """Generate a complete, executable FastAPI application for the following task.

Task:
{task}

Output only raw Python code."""

_FIX_TEMPLATE = """Fix the existing code based on the test failure log below.

Task:
{task}

Existing Code:
{code}

Test Failure Log:
{error_log}

Output only the complete fixed Python code."""


def coder_node(state: AgentState) -> AgentState:
    iteration = state.get("iteration", 0)
    print(f"\n[Coder Agent] Iteration {iteration + 1}")

    if not state.get("code"):
        prompt = _INITIAL_TEMPLATE.format(task=state["task"])
    else:
        prompt = _FIX_TEMPLATE.format(
            task=state["task"],
            code=state["code"],
            error_log=state["error_log"],
        )

    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    code = response.choices[0].message.content.strip()
    # Strip accidental markdown fences the model might include despite instructions
    if code.startswith("```"):
        lines = code.splitlines()
        code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    print(f"[Coder Agent] Code generated ({len(code)} chars)")
    return {**state, "code": code, "iteration": iteration + 1}
