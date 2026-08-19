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


## Summary

- **Total Tests:** 11

## Notes

- Tests use in-memory TripState (no API calls needed)
- Each test creates a fresh TripState instance

---
*Last updated: 2026-08-18*
