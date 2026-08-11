def get_road_distance(lat1, lon1, lat2, lon2):
    """Get road distance and duration between two points using OSRM."""
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
    params = {"overview": "false"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    if data.get("code") != "Ok":
        return {"error": data.get("message", "No route found")}

    route = data["routes"][0]
    return {
        "distance_km": round(route["distance"] / 1000, 1),
        "duration_min": round(route["duration"] / 60, 1),
    }