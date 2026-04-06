import os
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import build_graph
from state import AgentState

TASK = """Generate a Todo API with the following requirements:
- Todo entity with fields: id (int), title (str), completed (bool)
- CRUD endpoints:
  GET    /todos          → list all todos
  POST   /todos          → create a todo
  GET    /todos/{id}     → get a todo by id
  PUT    /todos/{id}     → update a todo
  DELETE /todos/{id}     → delete a todo
- Return 404 when a todo is not found
- In-memory storage (no database)
"""


def main():
    print("=" * 60)
    print("Mini Multi-Agent MVP")
    print("=" * 60)
    print(f"Task: {TASK.strip()}\n")

    initial_state: AgentState = {
        "task": TASK,
        "code": "",
        "test_code": "",
        "test_result": "",
        "error_log": "",
        "iteration": 0,
        "previous_error": "",
        "status": "running",
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print(f"Final Status : {final_state['status'].upper()}")
    print(f"Iterations   : {final_state['iteration']}")
    print(f"Test Result  : {final_state['test_result']}")
    print("=" * 60)

    if final_state["status"] == "success":
        print("\n[app.py saved to workspace/app.py]")
        print("[test_app.py saved to workspace/test_app.py]")
    else:
        print(f"\nLast error log:\n{final_state['error_log'][-1000:]}")


if __name__ == "__main__":
    main()
