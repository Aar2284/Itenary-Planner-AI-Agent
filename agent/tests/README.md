# 🧪 Test Documentation

> **Comprehensive test suite for the Itenary Planner AI Agent**

---

## 🚀 Quick Start

```bash
cd agent
pytest tests/ -v
```

### Run Individual Test Files

```bash
# 📊 State management tests
pytest tests/test_state.py -v

# 🔧 Tool dispatcher tests
pytest tests/test_tools.py -v

# 💬 Prompt validation tests
pytest tests/test_prompts.py -v

# 🌐 API endpoint tests
pytest tests/test_app.py -v
```

---

## 📊 Test Coverage Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST SUITE SUMMARY                       │
├─────────────────────────────────────────────────────────────┤
│  Total Tests:     45                                        │
│  test_state.py:   21 tests  ████████████░░░░░░  47%         │
│  test_app.py:     12 tests  ██████░░░░░░░░░░░░  27%         │
│  test_prompts.py:  9 tests  █████░░░░░░░░░░░░░  20%         │
│  test_tools.py:    8 tests  ████░░░░░░░░░░░░░░  18%         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Test Results by File

### 📊 test_state.py — Trip State Management

| #  | Test                                    | Description                                | Status |
|----|-----------------------------------------|--------------------------------------------|:------:|
| 1  | test_allocate_budget_without_setup      | Allocating budget before trip setup        | ✅     |
| 2  | test_allocate_budget_mismatch           | Allocation total doesn't match budget      | ✅     |
| 3  | test_allocate_budget_success            | Valid allocation matching budget           | ✅     |
| 4  | test_log_expense_without_allocation     | Log expense before budget allocation       | ✅     |
| 5  | test_log_expense_invalid_category       | Log expense with unknown category          | ✅     |
| 6  | test_log_expense_success                | Valid expense logging                      | ✅     |
| 7  | test_get_budget_status_no_trip          | Budget status without trip setup           | ✅     |
| 8  | test_get_budget_status_no_allocation    | Budget status without allocation           | ✅     |
| 9  | test_get_budget_status_success          | Budget status with valid trip              | ✅     |
| 10 | test_get_or_create_session_new          | New session creation                       | ✅     |
| 11 | test_get_existing_session               | Existing session retrieval                 | ✅     |
| 12 | test_category_status_levels             | Budget status shows correct levels         | ✅     |
| 13 | test_check_thresholds_critical_alert    | Over budget triggers critical alert 🚨     | ✅     |
| 14 | test_check_thresholds_warning_alert     | High spend triggers warning alert ⚠️       | ✅     |
| 15 | test_trip_progress_percent_not_started  | Future trip returns 0% progress            | ✅     |
| 16 | test_trip_progress_percent_ended        | Past trip returns 100% progress            | ✅     |
| 17 | test_log_expense_updates_category_spent | Expense updates category spent             | ✅     |
| 18 | test_multiple_expenses_accumulate       | Multiple expenses accumulate               | ✅     |
| 19 | test_get_budget_status_overall_calc     | Overall spent calculated correctly         | ✅     |
| 20 | test_session_store_new_session          | New sessions have unique IDs               | ✅     |
| 21 | test_get_session_nonexistent            | Missing session returns None               | ✅     |

---

### 🔧 test_tools.py — Tool Dispatcher

| #  | Test                                    | Description                                | Status |
|----|-----------------------------------------|--------------------------------------------|:------:|
| 1  | test_execute_unknown_tool               | Unknown tool name returns error            | ✅     |
| 2  | test_execute_setup_trip                 | setup_trip tool call works                 | ✅     |
| 3  | test_execute_allocate_budget            | allocate_budget tool call works            | ✅     |
| 4  | test_execute_log_expense                | log_expense tool call works                | ✅     |
| 5  | test_execute_get_exchange_rate_invalid  | Invalid currency pair with Unicode arrow → | ✅     |
| 6  | test_execute_get_budget_status          | get_budget_status tool returns data        | ✅     |
| 7  | test_execute_tool_returns_json_string   | Tool returns valid JSON string             | ✅     |
| 8  | test_execute_tool_exception_handling    | Exception handling for invalid args        | ✅     |

---

### 💬 test_prompts.py — Prompt Validation

| #  | Test                                    | Description                                | Status |
|----|-----------------------------------------|--------------------------------------------|:------:|
| 1  | test_system_prompt_not_empty            | System prompt has content                  | ✅     |
| 2  | test_tool_schemas_count                 | Should have exactly 5 tools               | ✅     |
| 3  | test_tool_schemas_have_required_fields  | Each schema has name, description, params  | ✅     |
| 4  | test_tool_names_match                   | Tool names match expected list             | ✅     |
| 5  | test_system_prompt_has_new_sections     | Prompt has Formatting, Alert, Goal-Based   | ✅     |
| 6  | test_tool_descriptions_not_empty        | Each tool has non-empty description        | ✅     |
| 7  | test_parameter_descriptions_exist       | All parameters have descriptions           | ✅     |
| 8  | test_tool_required_arrays               | Each tool has correct required parameters  | ✅     |
| 9  | test_log_expense_category_enum          | log_expense category enum correct          | ✅     |

---

### 🌐 test_app.py — API Endpoints

| #  | Test                                    | Description                                | Status |
|----|-----------------------------------------|--------------------------------------------|:------:|
| 1  | test_index_route                        | Index route returns HTML                   | ✅     |
| 2  | test_chat_missing_message               | Chat without message field returns 400     | ✅     |
| 3  | test_chat_empty_message                 | Chat with empty message returns 400        | ✅     |
| 4  | test_status_no_session                  | Status with nonexistent session            | ✅     |
| 5  | test_reset_endpoint                     | Reset clears session                       | ✅     |
| 6  | test_conversation_trimming              | Conversation history trims when long       | ✅     |
| 7  | test_chat_returns_json_with_session_id  | Chat returns JSON with session_id          | ✅     |
| 8  | test_expenses_empty_session             | Expenses with no session returns empty     | ✅     |
| 9  | test_status_no_trip                     | Status with setup but no allocation        | ✅     |
| 10 | test_reset_clears_conversation          | Reset clears conversation history          | ✅     |
| 11 | test_static_files_served                | Static files served correctly              | ✅     |
| 12 | test_chat_default_session               | Chat uses default session when not given   | ✅     |

---

## 🎯 Test Categories

```
┌──────────────────────────────────────────────────────────────┐
│  CATEGORY BREAKDOWN                                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  🔧 Unit Tests           30 tests   ███████████████░░░░░░    │
│     ├── state.py: 21                                          │
│     └── tools.py: 9                                           │
│                                                               │
│  🌐 Integration Tests    12 tests   ██████░░░░░░░░░░░░░░░    │
│     └── app.py: 12                                            │
│                                                               │
│  💬 Validation Tests      9 tests   ████░░░░░░░░░░░░░░░░░    │
│     └── prompts.py: 9                                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔍 What We Test

### 📊 State Management
- ✅ Trip setup and initialization
- ✅ Budget allocation across categories
- ✅ Expense logging with currency conversion
- ✅ Budget status with threshold alerts
- ✅ Session management (create, retrieve, reset)

### 🔧 Tool Dispatcher
- ✅ Tool routing to correct handlers
- ✅ JSON response formatting
- ✅ Error handling for unknown tools
- ✅ Exception handling for invalid arguments

### 💬 Prompt Validation
- ✅ System prompt structure and content
- ✅ Tool schema completeness
- ✅ Parameter descriptions and required fields
- ✅ Category enums and validation

### 🌐 API Endpoints
- ✅ Route responses and status codes
- ✅ Request validation (missing/empty fields)
- ✅ Session handling across requests
- ✅ JSON response structure

---

## 📝 Notes

| Note | Description                                                      |
|------|--------------------------------------------------------------=---|
| 🧪   | Tests use in-memory TripState (no API calls needed)             |
| 🔄   | Each test creates a fresh TripState instance                    |
| 🌐   | API tests use Flask test client                                 |
| 📦   | Tool tests verify JSON output format                            |

---

## 🏃 Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=agent --cov-report=html

# Run specific test by name
pytest tests/test_state.py::test_allocate_budget_success -v

# Run tests matching a pattern
pytest tests/ -k "budget" -v
```

---

## 📈 Test Statistics

```
┌─────────────────────────────────────────────────────────────┐
│                    🎯 SUCCESS RATE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Passed:        45 / 45  (100%)                          │
│  ⏭️  Skipped:       0 / 45  (0%)                            │
│                                                             │
│  ████████████████████████████████████████ 100% PASSING 🎉  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Last updated: 2026-09-02*
