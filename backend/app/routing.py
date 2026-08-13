"""
Real road-distance routing via OSRM (Open Source Routing Machine),
a free public routing API built on OpenStreetMap data -- no API key
required. Pairs naturally with Nominatim: Nominatim gets coordinates
from a name, OSRM gets the real road distance/time between two
coordinates, instead of a straight-line guess.

Note: router.project-osrm.org is a public demo server meant for
light/testing use -- fine for this project's scale, don't hammer it.
"""

import requests

OSRM_URL = "http://router.project-osrm.org/route/v1/driving"


def get_road_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """Real road distance (km) and driving duration (minutes) between two points."""
    coords = f"{lon1},{lat1};{lon2},{lat2}"
    url = f"{OSRM_URL}/{coords}"

    try:
        response = requests.get(url, params={"overview": "false"}, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {"error": f"Routing request failed: {e}"}

    if data.get("code") != "Ok" or not data.get("routes"):
        return {"error": f"OSRM could not find a route: {data.get('message', 'unknown error')}"}

    route = data["routes"][0]
    return {
        "distance_km": round(route["distance"] / 1000.0, 2),
        "duration_min": round(route["duration"] / 60.0, 1),
    }