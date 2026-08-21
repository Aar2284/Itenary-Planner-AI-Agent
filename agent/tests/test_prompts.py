"""Tests for prompt and tool schema validity."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.prompts import SYSTEM_PROMPT, TOOL_SCHEMAS


def test_system_prompt_not_empty():
    """System prompt should have content."""
    assert len(SYSTEM_PROMPT) > 100
    assert "TripBudgetBuddy" in SYSTEM_PROMPT


def test_tool_schemas_count():
    """Should have 5 tool schemas."""
    assert len(TOOL_SCHEMAS) == 5


def test_tool_schemas_have_required_fields():
    """Each tool schema should have name and parameters."""
    for schema in TOOL_SCHEMAS:
        assert schema["type"] == "function"
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]


def test_tool_names_match():
    """Tool names should match expected tools."""
    expected = ["setup_trip", "allocate_budget", "get_exchange_rate", "log_expense", "get_budget_status"]
    actual = [s["function"]["name"] for s in TOOL_SCHEMAS]
    assert actual == expected


if __name__ == "__main__":
    test_system_prompt_not_empty()
    test_tool_schemas_count()
    test_tool_schemas_have_required_fields()
    test_tool_names_match()
    print("All tests passed!")