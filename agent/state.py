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

    def allocate_budget(self, lodging: float, food: float, transport: float,
                        activities: float, shopping: float) -> dict:
        """Split total budget into categories."""
        if not self.is_setup:
            return {"status": "error", "message": "Please set up the trip first using setup_trip."}

        total_allocated = lodging + food + transport + activities + shopping
        total_budget = self.trip["total_budget"]

        if abs(total_allocated - total_budget) > 1:
            return {
                "status": "error",
                "message": (f"Allocation total ({total_allocated:.2f}) doesn't match "
                            f"trip budget ({total_budget:.2f}). Difference: "
                            f"{total_allocated - total_budget:.2f}. Please adjust.")
            }

        self.allocation = {
            "lodging": lodging,
            "food": food,
            "transport": transport,
            "activities": activities,
            "shopping": shopping
        }
        self.spent = {cat: 0.0 for cat in self.allocation}
        self.is_allocated = True

        return {
            "status": "success",
            "message": "Budget allocated across categories.",
            "allocation": self.allocation,
            "currency": self.trip["home_currency"]
        }

    def log_expense(self, category: str, amount_local: float, exchange_rate: float,
                    note: str = "") -> dict:
        """Record an expense, converting from local currency to home currency."""
        if not self.is_allocated:
            return {"status": "error", "message": "Please allocate the budget first."}

        category = category.lower()
        if category not in self.allocation:
            return {
                "status": "error",
                "message": f"Unknown category '{category}'. Valid: {list(self.allocation.keys())}"
            }

        amount_home = round(amount_local * exchange_rate, 2)

        expense = {
            "id": len(self.expenses) + 1,
            "category": category,
            "amount_local": amount_local,
            "local_currency": self.trip["local_currency"],
            "amount_home": amount_home,
            "home_currency": self.trip["home_currency"],
            "exchange_rate": exchange_rate,
            "note": note,
            "timestamp": datetime.now().isoformat()
        }
        self.expenses.append(expense)
        self.spent[category] += amount_home

        alerts = self._check_thresholds()

        result = {
            "status": "success",
            "expense_logged": expense,
            "category_spent": round(self.spent[category], 2),
            "category_budget": self.allocation[category],
            "category_remaining": round(self.allocation[category] - self.spent[category], 2),
            "category_percent_used": round((self.spent[category] / self.allocation[category]) * 100, 1)
        }

        if alerts:
            result["alerts"] = alerts

        return result