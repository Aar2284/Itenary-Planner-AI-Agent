"""
Tests for the agent's plan-act loop, using a mocked Groq client so
these run fast and deterministically without needing a real API key
or network access.

Important gotcha this test guards against: TOOL_FUNCTIONS captures
the actual function objects at import time, so patching
app.agent.get_distance directly does NOT affect what TOOL_FUNCTIONS
already points to. The fix is patch.dict on TOOL_FUNCTIONS itself.
"""

import sys
import os
import json
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("GROQ_API_KEY", "dummy-key-for-tests")

from app.agent import run_agent_turn
from app.memory import TripContext


def _fake_tool_call(name, arguments, call_id):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def _fake_response(tool_calls=None, content=None):
    msg = SimpleNamespace(tool_calls=tool_calls, content=content)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def test_multi_step_loop_and_memory_sync():
    step1 = _fake_response(tool_calls=[
        _fake_tool_call("get_distance", {"a": "Hawa Mahal", "b": "Amber Fort"}, "call_1")
    ])
    step2 = _fake_response(tool_calls=[
        _fake_tool_call("order_stops", {"stops": ["Hawa Mahal", "Amber Fort"]}, "call_2")
    ])
    step3 = _fake_response(content="Route: Hawa Mahal then Amber Fort, 9.2 km.")

    mock_get_distance = lambda a, b: {"from": a, "to": b, "distance_km": 9.2, "duration_min": 18.0}
    mock_order_stops = lambda stops, start=None: {
        "route": stops, "total_distance_km": 9.2, "total_duration_min": 18.0, "method": "nearest_neighbor"
    }

    with patch("app.agent.client.chat.completions.create", side_effect=[step1, step2, step3]), \
         patch.dict("app.agent.TOOL_FUNCTIONS", {"get_distance": mock_get_distance, "order_stops": mock_order_stops}):
        memory = TripContext()
        result = run_agent_turn("Plan a route through Hawa Mahal and Amber Fort", memory, verbose=False)

    assert result["reply"] == "Route: Hawa Mahal then Amber Fort, 9.2 km."
    assert len(result["trace"]) == 2
    assert result["trace"][0]["tool"] == "get_distance"
    assert result["trace"][1]["tool"] == "order_stops"
    # This is the actual proof memory works: the loop updated it mid-run.
    assert memory.current_route == ["Hawa Mahal", "Amber Fort"]
    assert memory.total_distance_km == 9.2
    print("Multi-step loop + memory sync  OK")


def test_zero_tool_calls_when_not_needed():
    with patch("app.agent.client.chat.completions.create",
               return_value=_fake_response(content="Hi, tell me some stops!")):
        memory = TripContext()
        result = run_agent_turn("hello", memory, verbose=False)
    assert result["reply"] == "Hi, tell me some stops!"
    assert result["trace"] == []
    print("Zero-tool-call turn (plain chat) handled correctly  OK")


def test_max_loop_steps_safety_cap():
    looping = _fake_response(tool_calls=[
        _fake_tool_call("get_distance", {"a": "A", "b": "B"}, "x")
    ])
    with patch("app.agent.client.chat.completions.create", return_value=looping), \
         patch.dict("app.agent.TOOL_FUNCTIONS", {"get_distance": lambda a, b: {"distance_km": 1, "duration_min": 1}}):
        memory = TripContext()
        result = run_agent_turn("loop forever", memory, verbose=False)
    assert "max steps" in result["reply"]
    assert len(result["trace"]) == 8
    print("MAX_LOOP_STEPS safety cap works  OK")


if __name__ == "__main__":
    test_multi_step_loop_and_memory_sync()
    test_zero_tool_calls_when_not_needed()
    test_max_loop_steps_safety_cap()
    print("\nAll agent loop tests passed (mocked Groq client).")