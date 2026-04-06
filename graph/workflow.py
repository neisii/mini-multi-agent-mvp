from typing import Literal
from langgraph.graph import StateGraph, END
from agents.coder_agent import coder_node
from agents.tester_agent import tester_node
from state import AgentState

MAX_ITERATIONS = 5


def should_continue(state: AgentState) -> Literal["coder", "end"]:
    if state["test_result"] == "SUCCESS":
        print("\n[Orchestrator] All tests passed. Done.")
        return "end"

    if state["iteration"] >= MAX_ITERATIONS:
        print(f"\n[Orchestrator] Max iterations ({MAX_ITERATIONS}) reached. Stopping.")
        return "end"

    if state.get("error_log") and state["error_log"] == state.get("previous_error", ""):
        print("\n[Orchestrator] Same error repeated. Stopping.")
        return "end"

    print(f"\n[Orchestrator] Tests failed. Retrying (iteration {state['iteration']}/{MAX_ITERATIONS})...")
    return "coder"


def _finalize(state: AgentState) -> AgentState:
    if state["test_result"] == "SUCCESS":
        status = "success"
    elif state["iteration"] >= MAX_ITERATIONS:
        status = "max_iterations"
    else:
        status = "repeated_error"
    return {**state, "status": status}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("coder", coder_node)
    graph.add_node("tester", tester_node)
    graph.add_node("finalize", _finalize)

    graph.set_entry_point("coder")
    graph.add_edge("coder", "tester")
    graph.add_conditional_edges(
        "tester",
        should_continue,
        {"coder": "coder", "end": "finalize"},
    )
    graph.add_edge("finalize", END)

    return graph.compile()
