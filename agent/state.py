"""
Trip State Management
---------------------
Manages the in-memory trip context that persists across the entire conversation.
"""

from datetime import datetime, date
import uuid


class TripState:
    """Holds all state for a single trip session."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.trip = None
        self.allocation = {}
        self.spent = {}
        self.expenses = []
        self.is_setup = False
        self.is_allocated = False

    def setup_trip(self, destination: str, home_currency: str, local_currency: str,
                   start_date: str, end_date: str, total_budget: float) -> dict:
        """Initialize trip parameters."""
        self.trip = {
            "destination": destination,
            "home_currency": home_currency.upper(),
            "local_currency": local_currency.upper(),
            "start_date": start_date,
            "end_date": end_date,
            "total_budget": total_budget
        }
        self.is_setup = True
        self.allocation = {}
        self.spent = {}
        self.expenses = []
        self.is_allocated = False
        return {
            "status": "success",
            "message": f"Trip to {destination} set up! Budget: {total_budget} {home_currency.upper()}",
            "trip": self.trip
        }