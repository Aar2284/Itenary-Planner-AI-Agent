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

### Live Agent Test (Groq LLM + tool calling)

```
$ python3 -c "
from app.agent import run_agent_turn
from app.memory import TripContext
memory = TripContext()
result = run_agent_turn('Plan a route through Hawa Mahal, Amber Fort, and City Palace in Jaipur', memory, verbose=True)
print('FINAL REPLY:', result['reply'])
"

[step 0] tool call: get_distance({'a': 'Hawa Mahal, Jaipur', 'b': 'Amber Fort, Jaipur'})
[step 0] tool result: {'distance_km': 9.01, 'duration_min': 12.4}

[step 1] tool call: get_distance({'a': 'Hawa Mahal, Jaipur', 'b': 'City Palace, Jaipur'})
[step 1] tool result: {'distance_km': 0.67, 'duration_min': 2.0}

[step 2] tool call: get_distance({'a': 'Amber Fort, Jaipur', 'b': 'City Palace, Jaipur'})
[step 2] tool result: {'distance_km': 9.37, 'duration_min': 14.7}

[step 3] tool call: order_stops({'start': 'Hawa Mahal, Jaipur', 'stops': ['Amber Fort, Jaipur', 'City Palace, Jaipur']})
[step 3] tool result: {'route': ['Hawa Mahal, Jaipur', 'City Palace, Jaipur', 'Amber Fort, Jaipur'], 'total_distance_km': 9.86, 'total_duration_min': 15.8}

FINAL REPLY: Recommended order: Hawa Mahal -> City Palace -> Amber Fort
Total: ~9.9 km, ~16 min driving
```

## Pytest Results

**Total: 20/20 passed**

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

### test_agent.py

| Test | Status |
|------|--------|
| `test_multi_step_loop_and_memory_sync` | PASSED |
| `test_zero_tool_calls_when_not_needed` | PASSED |
| `test_max_loop_steps_safety_cap` | PASSED |

---

*Last updated: 2026-08-15*
