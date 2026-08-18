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


## Summary

- **Total Tests:** 3

## Notes

- Tests use in-memory TripState (no API calls needed)
- Each test creates a fresh TripState instance

---
*Last updated: 2026-08-25*
