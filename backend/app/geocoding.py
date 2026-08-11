"""
Live geocoding via OpenStreetMap Nominatim (free, no API key required).
"""

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CSE476-RoutePlannerAgent/1.0 (student project)"

_geocode_cache: dict[str, tuple[float, float]] = {}


def normalize(name: str) -> str:
    return name.strip().lower()


def geocode(place: str) -> dict:
    """
    Look up a place name, return its latitude/longitude.
    Cached in-memory so repeated lookups don't re-hit the network
    and to respect Nominatim's rate-limit guidance.
    """
    key = normalize(place)
    if key in _geocode_cache:
        lat, lon = _geocode_cache[key]
        return {"place": place, "lat": lat, "lon": lon, "cached": True}

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=5,
        )
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as e:
        return {"error": f"Geocoding request failed for '{place}': {e}"}

    if not results:
        return {"error": f"Could not find a location for '{place}'."}

    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    _geocode_cache[key] = (lat, lon)

    return {"place": place, "lat": lat, "lon": lon, "cached": False}