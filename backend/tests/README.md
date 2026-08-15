# Test Results

## Live Test

```
$ python3 -c "from app.tools import get_distance; print(get_distance('Hawa Mahal, Jaipur', 'Amber Fort, Jaipur'))"

{'from': 'Hawa Mahal, Jaipur', 'to': 'Amber Fort, Jaipur', 'distance_km': 9.01, 'duration_min': 12.4}
```

### Real Landmark Route (order_stops)

```
$ python3 -c "
from app.tools import order_stops
result = order_stops(['Hawa Mahal, Jaipur', 'Amber Fort, Jaipur', 'City Palace, Jaipur', 'Nahargarh Fort, Jaipur'])
print(result)
"

{'route': ['Hawa Mahal, Jaipur', 'City Palace, Jaipur', 'Amber Fort, Jaipur', 'Nahargarh Fort, Jaipur'],
 'total_distance_km': 21.72,
 'total_duration_min': 42.6,
 'method': 'nearest_neighbor'}
```

## Pytest Results

**Total: 17/17 passed**

### test_geocoding.py

| Test | Status |
|------|--------|
| `test_geocode_returns_coords` | PASSED |
| `test_geocode_caches_repeated_lookups` | PASSED |
| `test_geocode_place_not_found` | PASSED |

### test_routing.py

| Test | Status |
|------|--------|
| `test_get_road_distance_success` | PASSED |
| `test_get_road_distance_no_route` | PASSED |

### test_tools.py

| Test | Status |
|------|--------|
| `test_get_distance_combines_geocode_and_route` | PASSED |
| `test_get_distance_propagates_geocode_error` | PASSED |
| `test_get_distance_propagates_routing_error` | PASSED |
| `test_order_stops_nearest_neighbor` | PASSED |
| `test_order_stops_propagates_distance_error` | PASSED |
| `test_order_stops_empty_list` | PASSED |
| `test_order_stops_single_stop_needs_no_calls` | PASSED |

### test_memory.py

| Test | Status |
|------|--------|
| `test_add_stop_no_duplicates` | PASSED |
| `test_mark_visited_removes_from_unvisited` | PASSED |
| `test_set_route_and_has_route` | PASSED |
| `test_summary_reflects_state` | PASSED |
| `test_summary_includes_duration_when_known` | PASSED |

---

*Last updated: 2026-08-14*
