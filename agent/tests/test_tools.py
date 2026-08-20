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


if __name__ == "__main__":
    test_execute_unknown_tool()
    test_execute_setup_trip()
    test_execute_allocate_budget()
    test_execute_log_expense()
    print("All tests passed!")