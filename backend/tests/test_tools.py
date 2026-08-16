"""
Tests for get_distance's orchestration logic. Mocks geocode and
get_road_distance directly (not requests.get) -- this tests HOW
tools.py combines the two layers, while the layers themselves are
already tested independently in test_geocoding.py / test_routing.py.
"""

import sys, os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tools import get_distance, order_stops, plan_days


def test_get_distance_combines_geocode_and_route():
    with patch("app.tools.geocode") as mock_geocode, \
         patch("app.tools.get_road_distance") as mock_route:
        mock_geocode.side_effect = [
            {"place": "Hawa Mahal", "lat": 26.9239, "lon": 75.8267, "cached": False},
            {"place": "Amber Fort", "lat": 26.9855, "lon": 75.8513, "cached": False},
        ]
        mock_route.return_value = {"distance_km": 9.2, "duration_min": 18.0}
        result = get_distance("Hawa Mahal", "Amber Fort")
    assert result["distance_km"] == 9.2
    assert result["duration_min"] == 18.0
    print("get_distance combines geocoding + routing  OK")


def test_get_distance_propagates_geocode_error():
    with patch("app.tools.geocode") as mock_geocode:
        mock_geocode.return_value = {"error": "Could not find a location for 'Atlantis'."}
        result = get_distance("Atlantis", "Hawa Mahal")
    assert "error" in result
    print("get_distance propagates a geocoding error  OK")


def test_get_distance_propagates_routing_error():
    with patch("app.tools.geocode") as mock_geocode, \
         patch("app.tools.get_road_distance") as mock_route:
        mock_geocode.side_effect = [
            {"place": "Hawa Mahal", "lat": 26.9239, "lon": 75.8267, "cached": False},
            {"place": "Amber Fort", "lat": 26.9855, "lon": 75.8513, "cached": False},
        ]
        mock_route.return_value = {"error": "OSRM could not find a route"}
        result = get_distance("Hawa Mahal", "Amber Fort")
    assert "error" in result
    print("get_distance propagates a routing error  OK")


def test_order_stops_nearest_neighbor():
    # Known distance matrix so the expected route is checkable by hand.
    distance_matrix = {
        frozenset(["A", "B"]): 5,
        frozenset(["A", "C"]): 3,
        frozenset(["A", "D"]): 10,
        frozenset(["B", "C"]): 4,
        frozenset(["B", "D"]): 6,
        frozenset(["C", "D"]): 2,
    }

    def mock_get_distance(a, b):
        d = distance_matrix[frozenset([a, b])]
        return {"from": a, "to": b, "distance_km": d, "duration_min": d * 2}

    with patch("app.tools.get_distance", side_effect=mock_get_distance):
        result = order_stops(["A", "B", "C", "D"], start="A")

    assert result["route"] == ["A", "C", "D", "B"]
    assert result["total_distance_km"] == 11
    assert result["total_duration_min"] == 22
    print(f"Nearest-neighbor route: {' -> '.join(result['route'])}  OK")


def test_order_stops_propagates_distance_error():
    with patch("app.tools.get_distance", return_value={"error": "not found"}):
        result = order_stops(["A", "B"])
    assert "error" in result
    print("order_stops propagates a distance error  OK")


def test_order_stops_empty_list():
    result = order_stops([])
    assert "error" in result
    print("Empty stop list handled gracefully  OK")


def test_order_stops_single_stop_needs_no_calls():
    with patch("app.tools.get_distance") as mock_gd:
        result = order_stops(["A"])
    assert result["route"] == ["A"]
    assert mock_gd.call_count == 0
    print("Single stop needs zero distance calls  OK")


def test_plan_days_fits_evenly():
    route = ["Hawa Mahal", "City Palace", "Amber Fort", "Nahargarh Fort"]
    result = plan_days(route, "2026-09-01", "2026-09-02", max_stops_per_day=2)
    assert result["fits"] is True
    assert result["num_days"] == 2
    assert result["day_plan"]["2026-09-01"] == ["Hawa Mahal", "City Palace"]
    print("plan_days splits evenly across days  OK")


def test_plan_days_uses_pace_default():
    route = ["Hawa Mahal", "City Palace", "Amber Fort"]
    result = plan_days(route, "2026-09-01", "2026-09-01", pace="packed")
    assert result["fits"] is True
    assert result["stops_per_day"] == 4
    print("plan_days falls back to pace default when max_stops_per_day omitted  OK")


def test_plan_days_reports_when_it_does_not_fit():
    route = ["Hawa Mahal", "City Palace", "Amber Fort", "Nahargarh Fort", "Jal Mahal"]
    result = plan_days(route, "2026-09-01", "2026-09-01", max_stops_per_day=2)
    assert result["fits"] is False
    assert result["excess_stops"] == ["Amber Fort", "Nahargarh Fort", "Jal Mahal"]
    print("plan_days reports shortfall instead of silently dropping stops  OK")


def test_plan_days_invalid_dates():
    result = plan_days(["Hawa Mahal"], "2026-09-05", "2026-09-01")
    assert "error" in result
    print("plan_days rejects end_date before start_date  OK")


def test_plan_days_malformed_date():
    result = plan_days(["Hawa Mahal"], "Sept 1", "2026-09-01")
    assert "error" in result
    print("plan_days rejects malformed date strings  OK")

    
if __name__ == "__main__":
    test_get_distance_combines_geocode_and_route()
    test_get_distance_propagates_geocode_error()
    test_get_distance_propagates_routing_error()
    test_order_stops_nearest_neighbor()
    test_order_stops_propagates_distance_error()
    test_order_stops_empty_list()
    test_order_stops_single_stop_needs_no_calls()
    print("\nAll tests passed.")