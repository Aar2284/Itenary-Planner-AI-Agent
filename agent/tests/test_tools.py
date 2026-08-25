"""Tests for tool dispatcher."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from agent.tools import execute_tool
from agent.state import TripState


def test_execute_unknown_tool():
    """Unknown tool name should return error."""
    state = TripState()
    result = execute_tool("unknown_tool", {}, state)
    parsed = json.loads(result)
    assert parsed["status"] == "error"
    assert "Unknown tool" in parsed["message"]


def test_execute_setup_trip():
    """setup_trip tool should initialize trip."""
    state = TripState()
    args = {
        "destination": "Tokyo",
        "home_currency": "USD",
        "local_currency": "JPY",
        "start_date": "2026-11-01",
        "end_date": "2026-11-10",
        "total_budget": 3000
    }
    result = execute_tool("setup_trip", args, state)
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert state.is_setup is True


def test_execute_allocate_budget():
    """allocate_budget tool should split budget."""
    state = TripState()
    state.setup_trip("Tokyo", "USD", "JPY", "2026-11-01", "2026-11-10", 3000)
    args = {"lodging": 1000, "food": 600, "transport": 400, "activities": 600, "shopping": 400}
    result = execute_tool("allocate_budget", args, state)
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert state.is_allocated is True


def test_execute_log_expense():
    """log_expense tool should record expense."""
    state = TripState()
    state.setup_trip("Tokyo", "USD", "JPY", "2026-11-01", "2026-11-10", 3000)
    state.allocate_budget(1000, 600, 400, 600, 400)
    args = {"category": "food", "amount_local": 1500, "exchange_rate": 0.0067, "note": "Ramen"}
    result = execute_tool("log_expense", args, state)
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert len(state.expenses) == 1


def test_execute_get_exchange_rate_invalid_pair():
    """Invalid currency pair should return error with Unicode arrow."""
    state = TripState()
    args = {"base_currency": "XYZ", "target_currency": "ABC"}
    result = execute_tool("get_exchange_rate", args, state)
    parsed = json.loads(result)
    assert parsed["status"] == "error"
    assert "→" in parsed["message"]


def test_execute_get_budget_status():
    """get_budget_status tool should return status."""
    state = TripState()
    state.setup_trip("Tokyo", "USD", "JPY", "2026-11-01", "2026-11-10", 3000)
    state.allocate_budget(1000, 600, 400, 600, 400)
    result = execute_tool("get_budget_status", {}, state)
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert "categories" in parsed


def test_execute_tool_returns_json_string():
    """execute_tool should return valid JSON string."""
    state = TripState()
    result = execute_tool("setup_trip", {
        "destination": "Paris",
        "home_currency": "EUR",
        "local_currency": "EUR",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
        "total_budget": 2000
    }, state)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_execute_tool_exception_handling():
    """execute_tool should handle exceptions gracefully."""
    state = TripState()
    result = execute_tool("setup_trip", {}, state)
    parsed = json.loads(result)
    assert parsed["status"] == "error"


if __name__ == "__main__":
    test_execute_unknown_tool()
    test_execute_setup_trip()
    test_execute_allocate_budget()
    test_execute_log_expense()
    test_execute_get_exchange_rate_invalid_pair()
    test_execute_get_budget_status()
    test_execute_tool_returns_json_string()
    test_execute_tool_exception_handling()
    print("All tests passed!")