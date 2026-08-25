import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.state import TripState, get_or_create_session, get_session


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


def test_category_status_levels():
    """Budget status should show correct status levels."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(10000, 10000, 10000, 10000, 10000)
    state.log_expense("food", 20000, 0.24, "Big dinner")
    result = state.get_budget_status()
    assert result["categories"]["food"]["status"] in ["critical", "warning", "over_budget"]


def test_check_thresholds_critical_alert():
    """Over budget should trigger critical alert."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(10000, 10000, 10000, 10000, 10000)
    state.log_expense("food", 50000, 0.24)
    result = state.get_budget_status()
    critical_alerts = [a for a in result["alerts"] if a["severity"] == "critical"]
    assert len(critical_alerts) > 0
    assert "OVER BUDGET" in critical_alerts[0]["message"]


def test_check_thresholds_warning_alert():
    """High spend with trip remaining should trigger warning alert."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-12-31", 50000)
    state.allocate_budget(10000, 10000, 10000, 10000, 10000)
    state.log_expense("food", 40000, 0.24)
    result = state.get_budget_status()
    warning_alerts = [a for a in result["alerts"] if a["severity"] == "warning"]
    assert len(warning_alerts) > 0


def test_trip_progress_percent_not_started():
    """Trip not started should return 0% progress."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-12-01", "2026-12-07", 50000)
    progress = state._trip_progress_percent()
    assert progress == 0.0


def test_trip_progress_percent_ended():
    """Trip ended should return 100% progress."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2020-01-01", "2020-01-07", 50000)
    progress = state._trip_progress_percent()
    assert progress == 100.0


def test_log_expense_updates_category_spent():
    """Logging expense should update category spent amount."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    state.log_expense("food", 500, 0.24)
    assert state.spent["food"] == 120.0


def test_multiple_expenses_accumulate():
    """Multiple expenses should accumulate in category."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    state.log_expense("food", 500, 0.24)
    state.log_expense("food", 500, 0.24)
    assert state.spent["food"] == 240.0
    assert len(state.expenses) == 2


def test_get_budget_status_overall_calculation():
    """Budget status should calculate overall spent correctly."""
    state = TripState()
    state.setup_trip("Bangkok", "INR", "THB", "2026-09-01", "2026-09-07", 50000)
    state.allocate_budget(15000, 10000, 8000, 10000, 7000)
    state.log_expense("food", 500, 0.24)
    state.log_expense("transport", 300, 0.24)
    result = state.get_budget_status()
    assert result["overall"]["total_spent"] == 192.0


def test_session_store_new_session():
    """New session should be created with unique ID."""
    state1 = get_or_create_session()
    state2 = get_or_create_session()
    assert state1.session_id != state2.session_id


def test_get_session_nonexistent():
    """Getting nonexistent session should return None."""
    result = get_session("nonexistent-id")
    assert result is None


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
    test_category_status_levels()
    test_check_thresholds_critical_alert()
    test_check_thresholds_warning_alert()
    test_trip_progress_percent_not_started()
    test_trip_progress_percent_ended()
    test_log_expense_updates_category_spent()
    test_multiple_expenses_accumulate()
    test_get_budget_status_overall_calculation()
    test_session_store_new_session()
    test_get_session_nonexistent()
    print("All tests passed!")