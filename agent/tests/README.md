# Test Documentation

## Overview

This folder contains unit tests for Itenary Planner AI Agent agent components.

## Running Tests

```bash
cd agent
pytest tests/test_state.py -v
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
| `test_setup_trip_invalid_budget` | Zero budget should fail | Error: "greater than zero" | PASSED |
| `test_setup_trip_dates_wrong_order` | End date before start date | Error: "Start date must be before" | PASSED |

### test_tools.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_execute_unknown_tool` | Unknown tool name | Error: "Unknown tool" | PASSED |
| `test_execute_setup_trip` | setup_trip tool call | Success, is_setup=True | PASSED |
| `test_execute_allocate_budget` | allocate_budget tool call | Success, is_allocated=True | PASSED |
| `test_execute_log_expense` | log_expense tool call | Success, 1 expense recorded | PASSED |

### test_prompts.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_system_prompt_not_empty` | System prompt has content | Length > 100, contains "TripBudgetBuddy" | PASSED |
| `test_tool_schemas_count` | Should have 5 tools | len == 5 | PASSED |
| `test_tool_schemas_have_required_fields` | Each schema has name, description, parameters | All fields present | PASSED |
| `test_tool_names_match` | Tool names match expected list | Exact match | PASSED |

### test_app.py

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| `test_index_route` | Index route returns HTML | Status 200 | PASSED |
| `test_chat_missing_message` | Chat without message field | Status 400 | PASSED |
| `test_chat_empty_message` | Chat with empty message | Status 400 | PASSED |
| `test_status_no_session` | Status with nonexistent session | "no_session" | PASSED |
| `test_reset_endpoint` | Reset clears session | "reset" status | PASSED |

## Summary

- **Total Tests:** 26

## Notes

- Tests use in-memory TripState (no API calls needed)
- Each test creates a fresh TripState instance

---
*Last updated: 2026-08-22*
