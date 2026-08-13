"""Tests for routing.py in isolation."""

import sys, os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.routing import get_road_distance


def test_get_road_distance_success():
    with patch("app.routing.requests.get") as mock_get:
        r = MagicMock(); r.raise_for_status = MagicMock()
        r.json.return_value = {"code": "Ok", "routes": [{"distance": 9200, "duration": 1080}]}
        mock_get.return_value = r
        result = get_road_distance(26.9239, 75.8267, 26.9855, 75.8513)
    assert result["distance_km"] == 9.2
    assert result["duration_min"] == 18.0
    print("get_road_distance returns real road distance/time  OK")


def test_get_road_distance_no_route():
    with patch("app.routing.requests.get") as mock_get:
        r = MagicMock(); r.raise_for_status = MagicMock()
        r.json.return_value = {"code": "NoRoute", "message": "no route found"}
        mock_get.return_value = r
        result = get_road_distance(0, 0, 90, 90)
    assert "error" in result
    print("get_road_distance handles no-route case  OK")


if __name__ == "__main__":
    test_get_road_distance_success()
    test_get_road_distance_no_route()
    print("\nAll routing tests passed.")