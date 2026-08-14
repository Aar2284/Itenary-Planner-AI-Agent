"""
Memory: the state that persists across turns in the same conversation.

This is what separates the agent from a stateless chatbot. Without
this class, every message would be independent -- the agent would
have no idea what stops you'd already given it, which ones you'd
already visited, or what the last computed route was.

In the FastAPI layer (added later), one TripContext instance will be
kept per session_id, so multiple users/conversations don't share
state with each other.
"""


class TripContext:
    def __init__(self):
        self.stops_added: list[str] = []      # every stop the user has mentioned
        self.visited: set[str] = set()         # stops marked "already been there"
        self.current_route: list[str] = []     # last computed order_stops() result
        self.total_distance_km: float | None = None
        self.total_duration_min: float | None = None
        self.main_place: str | None = None     # optional fixed start point

    # ---- mutation methods: how the agent updates memory ----

    def add_stop(self, place: str):
        if place not in self.stops_added:
            self.stops_added.append(place)

    def mark_visited(self, place: str):
        self.visited.add(place)
        if place in self.stops_added:
            self.stops_added.remove(place)

    def set_route(self, route: list[str], total_distance_km: float, total_duration_min: float = None):
        self.current_route = route
        self.total_distance_km = total_distance_km
        self.total_duration_min = total_duration_min

    # ---- read methods: how the agent reads memory back ----

    def unvisited_stops(self) -> list[str]:
        return [s for s in self.stops_added if s not in self.visited]

    def has_route(self) -> bool:
        return len(self.current_route) > 0

    def summary(self) -> str:
        """
        A plain-text summary injected into the LLM's context every
        turn, so the model can "read back" what it already knows
        without the conversation re-explaining itself each time.
        This string IS the memory, as far as the model is concerned.
        """
        lines = []
        lines.append(f"Stops mentioned so far: {self.stops_added or 'none'}")
        lines.append(f"Already visited (exclude from routing): {sorted(self.visited) or 'none'}")
        if self.has_route():
            duration_part = f", ~{self.total_duration_min} min driving" if self.total_duration_min else ""
            lines.append(
                f"Last computed route: {' -> '.join(self.current_route)} "
                f"(total {self.total_distance_km} km{duration_part})"
            )
        else:
            lines.append("No route has been computed yet.")
        return "\n".join(lines)