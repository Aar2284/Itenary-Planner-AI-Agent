"""Tests for TripState - budget allocation validation."""

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