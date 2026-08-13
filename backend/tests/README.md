# Test Results

## Live Test

```
$ python3 -c "from app.tools import get_distance; print(get_distance('Hawa Mahal, Jaipur', 'Amber Fort, Jaipur'))"

{'from': 'Hawa Mahal, Jaipur', 'to': 'Amber Fort, Jaipur', 'distance_km': 9.01, 'duration_min': 12.4}
```

## Pytest Results

**Total: 8/8 passed**

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

---

*Last updated: 2026-08-24*
