"""Tests for geocoding.py in isolation -- one network layer at a time."""

import sys, os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import geocoding


def _mock_response(lat, lon):
    r = MagicMock()
    r.raise_for_status = MagicMock()
    r.json.return_value = [{"lat": str(lat), "lon": str(lon)}]
    return r


def test_geocode_returns_coords():
    geocoding._geocode_cache.clear()
    with patch("app.geocoding.requests.get") as mock_get:
        mock_get.return_value = _mock_response(26.9239, 75.8267)
        result = geocoding.geocode("Hawa Mahal")
    assert result["lat"] == 26.9239
    print("geocode returns coordinates  OK")


def test_geocode_caches_repeated_lookups():
    geocoding._geocode_cache.clear()
    with patch("app.geocoding.requests.get") as mock_get:
        mock_get.return_value = _mock_response(26.9239, 75.8267)
        geocoding.geocode("Hawa Mahal")
        geocoding.geocode("Hawa Mahal")
    assert mock_get.call_count == 1
    print("geocode caches repeated lookups  OK")


def test_geocode_place_not_found():
    geocoding._geocode_cache.clear()
    with patch("app.geocoding.requests.get") as mock_get:
        r = MagicMock(); r.raise_for_status = MagicMock(); r.json.return_value = []
        mock_get.return_value = r
        result = geocoding.geocode("Atlantis")
    assert "error" in result
    print("geocode handles unknown place  OK")


if __name__ == "__main__":
    test_geocode_returns_coords()
    test_geocode_caches_repeated_lookups()
    test_geocode_place_not_found()
    print("\nAll geocoding tests passed.")