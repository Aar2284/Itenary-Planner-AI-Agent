# Test Documentation

## Overview

This folder contains unit tests for Itenary Planner AI Agent components.

## Running Tests

```bash
cd agent
pytest tests/ -v
```

Or run individual test files:

```bash
pytest tests/test_state.py -v
pytest tests/test_tools.py -v
pytest tests/test_prompts.py -v
pytest tests/test_app.py -v
```

## Test Results

### test_state.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_allocate_budget_without_setup` | Allocating budget before trip setup | Error: "set up the trip first" | PASSED |
| `test_allocate_budget_mismatch` | Allocation total doesn't match budget | Error: "doesn't match" | PASSED |
| `test_allocate_budget_success` | Valid allocation matching budget | Success, is_allocated=True | PASSED |
| `test_log_expense_without_allocation` | Log expense before budget allocation | Error: "allocate the budget first" | PASSED |
| `test_log_expense_invalid_category` | Log expense with unknown category | Error: "Unknown category" | PASSED |
| `test_log_expense_success` | Valid expense logging | Success, amount_home=120.0 | PASSED |
| `test_get_budget_status_no_trip` | Budget status without trip setup | Error: "No trip set up yet" | PASSED |
| `test_get_budget_status_no_allocation` | Budget status without allocation | Error: "Budget not allocated yet" | PASSED |
| `test_get_budget_status_success` | Budget status with valid trip | Success, total_budget=50000 | PASSED |
| `test_get_or_create_session_new` | New session creation | session_id matches, is_setup=False | PASSED |
| `test_get_existing_session` | Existing session retrieval | Returns same session, is_setup=True | PASSED |
| `test_category_status_levels` | Budget status shows correct levels | status in critical/warning/over_budget | PASSED |
| `test_check_thresholds_critical_alert` | Over budget triggers critical alert | Critical alert with "OVER BUDGET" | PASSED |
| `test_check_thresholds_warning_alert` | High spend triggers warning alert | Warning alert present | PASSED |
| `test_trip_progress_percent_not_started` | Future trip returns 0% progress | progress == 0.0 | PASSED |
| `test_trip_progress_percent_ended` | Past trip returns 100% progress | progress == 100.0 | PASSED |
| `test_log_expense_updates_category_spent` | Expense updates category spent | spent[food] == 120.0 | PASSED |
| `test_multiple_expenses_accumulate` | Multiple expenses accumulate | spent[food] == 240.0, 2 expenses | PASSED |
| `test_get_budget_status_overall_calculation` | Overall spent calculated correctly | total_spent == 192.0 | PASSED |
| `test_session_store_new_session` | New sessions have unique IDs | session_id1 != session_id2 | PASSED |
| `test_get_session_nonexistent` | Missing session returns None | result is None | PASSED |

### test_tools.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_execute_unknown_tool` | Unknown tool name | Error: "Unknown tool" | PASSED |
| `test_execute_setup_trip` | setup_trip tool call | Success, is_setup=True | PASSED |
| `test_execute_allocate_budget` | allocate_budget tool call | Success, is_allocated=True | PASSED |
| `test_execute_log_expense` | log_expense tool call | Success, 1 expense recorded | PASSED |
| `test_execute_get_exchange_rate_invalid_pair` | Invalid currency pair | Error with "→" Unicode arrow | PASSED |
| `test_execute_get_budget_status` | get_budget_status tool call | Success, categories present | PASSED |
| `test_execute_tool_returns_json_string` | Tool returns valid JSON string | isinstance(result, str) | PASSED |
| `test_execute_tool_exception_handling` | Exception handling for invalid args | Error status returned | PASSED |

### test_prompts.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_system_prompt_not_empty` | System prompt has content | Length > 100, contains "TripBudgetBuddy" | PASSED |
| `test_tool_schemas_count` | Should have 5 tools | len == 5 | PASSED |
| `test_tool_schemas_have_required_fields` | Each schema has name, description, parameters | All fields present | PASSED |
| `test_tool_names_match` | Tool names match expected list | Exact match | PASSED |
| `test_system_prompt_has_new_sections` | Prompt has Formatting, Alert Behavior, Goal-Based Reasoning | All sections present | PASSED |
| `test_tool_descriptions_not_empty` | Each tool has non-empty description | len > 10 | PASSED |
| `test_parameter_descriptions_exist` | All parameters have descriptions | "description" in param_def | PASSED |
| `test_tool_required_arrays` | Each tool has correct required parameters | Exact match | PASSED |
| `test_log_expense_category_enum` | log_expense category enum correct | Enum matches expected values | PASSED |

### test_app.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_index_route` | Index route returns HTML | Status 200 | PASSED |
| `test_chat_missing_message` | Chat without message field | Status 400 | PASSED |
| `test_chat_empty_message` | Chat with empty message | Status 400 | PASSED |
| `test_status_no_session` | Status with nonexistent session | "no_session" | PASSED |
| `test_reset_endpoint` | Reset clears session | "reset" status | PASSED |
| `test_conversation_trimming` | Conversation history trims when long | len > 50 check | PASSED |
| `test_chat_returns_json_with_session_id` | Chat returns JSON with session_id | response and session_id present | PASSED |
| `test_expenses_empty_session` | Expenses with no session | Empty list returned | PASSED |
| `test_status_no_trip` | Status with setup but no allocation | "no_trip" status | PASSED |
| `test_reset_clears_conversation` | Reset clears conversation history | Session removed from conversations | PASSED |
| `test_static_files_served` | Static files served correctly | Status 404 for nonexistent | PASSED |
| `test_chat_default_session` | Chat uses default session | session_id == "default" | PASSED |

## Summary

- **Total Tests:** 45
- **test_state.py:** 21 tests
- **test_tools.py:** 8 tests
- **test_prompts.py:** 9 tests
- **test_app.py:** 12 tests (including 6 new tests)

## Notes

- Tests use in-memory TripState (no API calls needed)
- Each test creates a fresh TripState instance
- API endpoint tests use Flask test client
- Tool dispatcher tests verify JSON output format

---
*Last updated: 2026-08-31*
