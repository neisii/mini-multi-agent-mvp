import os
import subprocess
import sys
from pathlib import Path
from openai import OpenAI
from state import AgentState

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

WORKSPACE = Path(__file__).parent.parent / "workspace"

_SYSTEM_PROMPT = """You are a Tester Agent. Your job is to generate pytest test cases for a FastAPI application.

Rules:
- Output ONLY raw Python code — no markdown, no code fences, no explanations
- Use FastAPI's TestClient: from starlette.testclient import TestClient
- Import the app as: from app import app
- Must include at least one test per CRUD endpoint
- All tests must be executable without a running server
"""

_TEST_TEMPLATE = """Generate complete pytest test cases for the following FastAPI application.

Application Code:
{code}

Output only raw Python test code."""


def tester_node(state: AgentState) -> AgentState:
    print("\n[Tester Agent] Generating test code...")

    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _TEST_TEMPLATE.format(code=state["code"])},
        ],
        temperature=0.2,
    )

    test_code = response.choices[0].message.content.strip()
    if test_code.startswith("```"):
        lines = test_code.splitlines()
        test_code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    WORKSPACE.mkdir(exist_ok=True)
    (WORKSPACE / "app.py").write_text(state["code"])
    (WORKSPACE / "test_app.py").write_text(test_code)

    print("[Tester Agent] Running tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_app.py", "-v", "--tb=short"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    test_result = "SUCCESS" if result.returncode == 0 else "FAIL"
    print(f"[Tester Agent] Result: {test_result}")
    if test_result == "FAIL":
        print(f"[Tester Agent] Error log:\n{output[-2000:]}")

    return {
        **state,
        "test_code": test_code,
        "test_result": test_result,
        "previous_error": state.get("error_log", ""),
        "error_log": output if test_result == "FAIL" else "",
    }
