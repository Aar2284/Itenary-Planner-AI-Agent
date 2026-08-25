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


def test_system_prompt_has_new_sections():
    """System prompt should contain new behavioral sections."""
    assert "Formatting" in SYSTEM_PROMPT
    assert "Alert Behavior" in SYSTEM_PROMPT
    assert "Goal-Based Reasoning" in SYSTEM_PROMPT


def test_tool_descriptions_not_empty():
    """Each tool should have a non-empty description."""
    for schema in TOOL_SCHEMAS:
        assert len(schema["function"]["description"]) > 10


def test_parameter_descriptions_exist():
    """All parameters should have descriptions."""
    for schema in TOOL_SCHEMAS:
        params = schema["function"]["parameters"]
        if params.get("properties"):
            for param_name, param_def in params["properties"].items():
                assert "description" in param_def, f"Missing description for {param_name}"


def test_tool_required_arrays():
    """Each tool should have correct required parameters."""
    expected_required = {
        "setup_trip": ["destination", "home_currency", "local_currency", "start_date", "end_date", "total_budget"],
        "allocate_budget": ["lodging", "food", "transport", "activities", "shopping"],
        "get_exchange_rate": ["base_currency", "target_currency"],
        "log_expense": ["category", "amount_local", "exchange_rate"],
        "get_budget_status": []
    }
    for schema in TOOL_SCHEMAS:
        name = schema["function"]["name"]
        assert schema["function"]["parameters"]["required"] == expected_required[name]


def test_log_expense_category_enum():
    """log_expense category should have correct enum values."""
    log_expense_schema = TOOL_SCHEMAS[3]
    categories = log_expense_schema["function"]["parameters"]["properties"]["category"]["enum"]
    assert categories == ["lodging", "food", "transport", "activities", "shopping"]


if __name__ == "__main__":
    test_system_prompt_not_empty()
    test_tool_schemas_count()
    test_tool_schemas_have_required_fields()
    test_tool_names_match()
    test_system_prompt_has_new_sections()
    test_tool_descriptions_not_empty()
    test_parameter_descriptions_exist()
    test_tool_required_arrays()
    test_log_expense_category_enum()
    print("All tests passed!")