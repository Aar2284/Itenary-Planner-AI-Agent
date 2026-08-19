import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.state import TripState


def test_allocate_budget_without_setup():
    """Allocate budget before trip setup should fail."""
    state = TripState()
    result = state.allocate_budget(100, 100, 100, 100, 100)
    assert result["status"] == "error"
    assert "set up the trip first" in result["message"]


def test_allocate_budget_mismatch():
    """Allocation total not matching budget should fail."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    result = state.allocate_budget(10000, 10000, 10000, 10000, 5000)
    assert result["status"] == "error"
    assert "doesn't match" in result["message"]


def test_allocate_budget_success():
    """Valid allocation should succeed."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    result = state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    assert result["status"] == "success"
    assert state.is_allocated is True
    assert len(state.allocation) == 5


def test_log_expense_without_allocation():
    """Log expense before budget allocation should fail."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    result = state.log_expense("food", 500, 0.24)
    assert result["status"] == "error"
    assert "allocate the budget first" in result["message"]


def test_log_expense_invalid_category():
    """Log expense with unknown category should fail."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    result = state.log_expense("alcohol", 500, 0.24)
    assert result["status"] == "error"
    assert "Unknown category" in result["message"]


def test_log_expense_success():
    """Valid expense logging should succeed."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    result = state.log_expense("food", 500, 0.24, "Lunch at street market")
    assert result["status"] == "success"
    assert result["expense_logged"]["amount_home"] == 120.0
    assert len(state.expenses) == 1

def test_get_budget_status_no_trip():
    """Budget status without trip setup should fail."""
    state = TripState()
    result = state.get_budget_status()
    assert result["status"] == "error"
    assert "No trip set up yet" in result["message"]


def test_get_budget_status_no_allocation():
    """Budget status without allocation should fail."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    result = state.get_budget_status()
    assert result["status"] == "error"
    assert "Budget not allocated yet" in result["message"]


def test_get_budget_status_success():
    """Budget status with valid trip and allocation should succeed."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    result = state.get_budget_status()
    assert result["status"] == "success"
    assert result["overall"]["total_budget"] == 50000
    assert result["overall"]["total_spent"] == 0
    assert len(result["categories"]) == 5

def test_get_or_create_session_new():
    """New session should be created when none exists."""
    state = get_or_create_session("test-session-1")
    assert state.session_id == "test-session-1"
    assert state.is_setup is False


def test_get_existing_session():
    """Existing session should be returned."""
    state = get_or_create_session("test-session-2")
    state.setup_trip("Paris", "EUR", "EUR", "2026-10-01", "2026-10-05", 2000)
    same = get_session("test-session-2")
    assert same is not None
    assert same.is_setup is True


if __name__ == "__main__":
    test_allocate_budget_without_setup()
    test_allocate_budget_mismatch()
    test_allocate_budget_success()
    test_log_expense_without_allocation()
    test_log_expense_invalid_category()
    test_log_expense_success()
    test_get_budget_status_no_trip()
    test_get_budget_status_no_allocation()
    test_get_budget_status_success()
    test_get_or_create_session_new()
    test_get_existing_session()
    print("All tests passed!")