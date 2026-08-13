"""
Tests for get_distance's orchestration logic. Mocks geocode and
get_road_distance directly (not requests.get) -- this tests HOW
tools.py combines the two layers, while the layers themselves are
already tested independently in test_geocoding.py / test_routing.py.
"""

import sys, os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tools import get_distance


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


if __name__ == "__main__":
    test_get_distance_combines_geocode_and_route()
    test_get_distance_propagates_geocode_error()
    test_get_distance_propagates_routing_error()
    print("\nAll get_distance orchestration tests passed.")