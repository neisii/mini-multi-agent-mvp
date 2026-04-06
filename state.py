from typing import TypedDict


class AgentState(TypedDict):
    task: str
    code: str
    test_code: str
    test_result: str      # "SUCCESS" | "FAIL" | ""
    error_log: str
    iteration: int
    previous_error: str
    status: str           # "running" | "success" | "max_iterations" | "repeated_error"
