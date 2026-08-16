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


def order_stops(stops: list, start: str = None) -> dict:
    """
    Given a list of place names, return a sensible visiting order
    using real road distances (via get_distance, which itself uses
    Nominatim for coordinates and OSRM for road distance/time).

    Algorithm: nearest-neighbor heuristic -- same reasoning as a
    straight-line version would use, just backed by real road data
    now. Each step calls get_distance from the current stop to every
    remaining stop and picks the closest, so for n stops this makes
    up to n*(n-1)/2 live network calls in the worst case. That's fine
    for this project's scale (a handful of stops), but worth knowing
    -- router.project-osrm.org is a public, rate-limited demo server,
    not built for heavy traffic.
    """
    if not stops:
        return {"error": "No stops provided."}

    remaining = list(stops)
    current = start if start else remaining[0]
    if current not in remaining:
        remaining.insert(0, current)
    remaining.remove(current)

    route = [current]
    total_distance_km = 0.0
    total_duration_min = 0.0

    while remaining:
        distances = {}
        for place in remaining:
            result = get_distance(current, place)
            if "error" in result:
                return {
                    "error": (
                        f"Could not compute distance from '{current}' to "
                        f"'{place}': {result['error']}"
                    )
                }
            distances[place] = result

        nearest = min(distances, key=lambda p: distances[p]["distance_km"])
        leg = distances[nearest]
        total_distance_km += leg["distance_km"]
        total_duration_min += leg["duration_min"]

        route.append(nearest)
        remaining.remove(nearest)
        current = nearest

    return {
        "route": route,
        "total_distance_km": round(total_distance_km, 2),
        "total_duration_min": round(total_duration_min, 1),
        "method": "nearest_neighbor",
    }


# Pace -> how many stops feel reasonable in one day. This is only a
# fallback default; real usage has the agent ask the user about their
# preferred pace via conversation and pass max_stops_per_day
# explicitly (see agent.py's elicitation instructions, added later).
PACE_STOPS_PER_DAY = {
    "relaxed": 2,
    "moderate": 3,
    "packed": 4,
}


def plan_days(route: list, start_date: str, end_date: str,
              pace: str = "moderate", max_stops_per_day: int = None) -> dict:
    """
    Split an already-ordered route (from order_stops) across the days
    of a trip, given a start and end date ("YYYY-MM-DD" strings).

    This is the "must be agentic" check for the date-aware part of
    the project: it decides whether the route actually FITS the
    available days and says so explicitly, rather than silently
    cramming everything in or silently dropping stops.
    """
    from datetime import date

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return {"error": "Dates must be in YYYY-MM-DD format."}

    if end < start:
        return {"error": "end_date must be on or after start_date."}

    num_days = (end - start).days + 1

    if max_stops_per_day is None:
        max_stops_per_day = PACE_STOPS_PER_DAY.get(pace, PACE_STOPS_PER_DAY["moderate"])

    capacity = num_days * max_stops_per_day

    if len(route) > capacity:
        return {
            "fits": False,
            "num_days": num_days,
            "stops_per_day": max_stops_per_day,
            "capacity": capacity,
            "total_stops": len(route),
            "excess_stops": route[capacity:],
            "message": (
                f"{len(route)} stops don't fit in {num_days} day(s) at "
                f"{max_stops_per_day} stops/day (capacity {capacity}). "
                f"{len(route) - capacity} stop(s) would need to be dropped, "
                f"or the trip extended, or the pace increased."
            ),
        }

    day_plan = {}
    for i in range(num_days):
        chunk = route[i * max_stops_per_day: (i + 1) * max_stops_per_day]
        if not chunk:
            break
        day_key = (start.fromordinal(start.toordinal() + i)).isoformat()
        day_plan[day_key] = chunk

    return {
        "fits": True,
        "num_days": num_days,
        "stops_per_day": max_stops_per_day,
        "day_plan": day_plan,
    }