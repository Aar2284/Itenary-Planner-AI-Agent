"""
The tools the agent calls.

get_distance is layered: geocoding.py (name -> coords), routing.py
(coords -> real road distance/time), this file (combines them into
the one tool the agent sees). Each layer is independently testable
and independently replaceable.
"""

from app.geocoding import geocode
from app.routing import get_road_distance


def get_distance(a: str, b: str) -> dict:
    """Real road distance (km) and driving time (min) between two named places."""
    geo_a = geocode(a)
    if "error" in geo_a:
        return {"error": geo_a["error"]}

    geo_b = geocode(b)
    if "error" in geo_b:
        return {"error": geo_b["error"]}

    route = get_road_distance(geo_a["lat"], geo_a["lon"], geo_b["lat"], geo_b["lon"])
    if "error" in route:
        return {"error": route["error"]}

    return {
        "from": a,
        "to": b,
        "distance_km": route["distance_km"],
        "duration_min": route["duration_min"],
    }