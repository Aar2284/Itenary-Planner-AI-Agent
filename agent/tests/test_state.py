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


if __name__ == "__main__":
    test_allocate_budget_without_setup()
    test_allocate_budget_mismatch()
    test_allocate_budget_success()
    test_log_expense_without_allocation()
    test_log_expense_invalid_category()
    test_log_expense_success()
    print("All tests passed!")