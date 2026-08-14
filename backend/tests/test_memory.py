"""
Standalone tests for memory.TripContext -- tested before the LLM or
API layer touches it, so bugs are unambiguous.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.memory import TripContext


def test_add_stop_no_duplicates():
    ctx = TripContext()
    ctx.add_stop("Hawa Mahal")
    ctx.add_stop("Hawa Mahal")
    assert ctx.stops_added == ["Hawa Mahal"]
    print("No duplicate stops  OK")


def test_mark_visited_removes_from_unvisited():
    ctx = TripContext()
    ctx.add_stop("Hawa Mahal")
    ctx.add_stop("Amber Fort")
    ctx.mark_visited("Hawa Mahal")
    assert ctx.unvisited_stops() == ["Amber Fort"]
    assert "Hawa Mahal" in ctx.visited
    print("mark_visited updates unvisited_stops  OK")


def test_set_route_and_has_route():
    ctx = TripContext()
    assert ctx.has_route() is False
    ctx.set_route(["A", "B", "C"], 12.5, 25.0)
    assert ctx.has_route() is True
    assert ctx.total_distance_km == 12.5
    assert ctx.total_duration_min == 25.0
    print("set_route / has_route  OK")


def test_summary_reflects_state():
    ctx = TripContext()
    ctx.add_stop("Hawa Mahal")
    ctx.mark_visited("Hawa Mahal")
    summary = ctx.summary()
    assert "Hawa Mahal" in summary
    print("summary() reflects current state  OK")


def test_summary_includes_duration_when_known():
    ctx = TripContext()
    ctx.set_route(["A", "B"], 9.2, 18.0)
    summary = ctx.summary()
    assert "18.0 min driving" in summary
    print("summary() includes driving duration  OK")


if __name__ == "__main__":
    test_add_stop_no_duplicates()
    test_mark_visited_removes_from_unvisited()
    test_set_route_and_has_route()
    test_summary_reflects_state()
    test_summary_includes_duration_when_known()
    print("\nAll memory tests passed.")