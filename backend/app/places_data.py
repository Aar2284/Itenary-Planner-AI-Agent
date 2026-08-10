PLACES_DB = {
    "new_york": [
        {"id": "ny1", "name": "Central Park", "type": "park", "lat": 40.7829, "lng": -73.9654},
        {"id": "ny2", "name": "Times Square", "type": "landmark", "lat": 40.7580, "lng": -73.9855},
        {"id": "ny3", "name": "Statue of Liberty", "type": "monument", "lat": 40.6892, "lng": -74.0445},
    ],
    "paris": [
        {"id": "par1", "name": "Eiffel Tower", "type": "landmark", "lat": 48.8584, "lng": 2.2945},
        {"id": "par2", "name": "Louvre Museum", "type": "museum", "lat": 48.8606, "lng": 2.3376},
        {"id": "par3", "name": "Notre Dame", "type": "cathedral", "lat": 48.8530, "lng": 2.3499},
    ],
}


def get_places_by_city(city: str) -> list:
    return PLACES_DB.get(city.lower(), [])


def search_local_places(query: str) -> list:
    results = []
    for city_places in PLACES_DB.values():
        for place in city_places:
            if query.lower() in place["name"].lower():
                results.append(place)
    return results
