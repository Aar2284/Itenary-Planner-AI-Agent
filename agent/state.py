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

    def _check_thresholds(self) -> list:
        """fires alerts based on spending vs remaining trip time."""
        alerts = []
        trip_progress = self._trip_progress_percent()
        trip_remaining = 100 - trip_progress

        for cat, budget in self.allocation.items():
            if budget <= 0:
                continue
            spent = self.spent[cat]
            pct_used = (spent / budget) * 100

            if spent > budget:
                overspend = spent - budget
                alerts.append({
                    "severity": "critical",
                    "category": cat,
                    "message": (f"OVER BUDGET: {cat.title()} is {overspend:.2f} "
                                f"{self.trip['home_currency']} over budget!")
                })
            elif pct_used >= 85 and trip_remaining > 20:
                alerts.append({
                    "severity": "warning",
                    "category": cat,
                    "message": (f"{cat.title()} is {pct_used:.0f}% spent but "
                                f"{trip_remaining:.0f}% of your trip remains.")
                })
            elif pct_used >= 70 and pct_used > trip_progress + 15:
                alerts.append({
                    "severity": "info",
                    "category": cat,
                    "message": (f"{cat.title()} spending ({pct_used:.0f}%) is "
                                f"outpacing trip progress ({trip_progress:.0f}%).")
                })

        return alerts

    def _trip_progress_percent(self) -> float:
        """Calculate what percentage of the trip has elapsed."""
        if not self.trip:
            return 0.0
        try:
            start = date.fromisoformat(self.trip["start_date"])
            end = date.fromisoformat(self.trip["end_date"])
            today = date.today()

            if today <= start:
                return 0.0
            if today >= end:
                return 100.0

            total_days = (end - start).days
            elapsed = (today - start).days
            return round((elapsed / total_days) * 100, 1) if total_days > 0 else 0.0
        except (ValueError, KeyError):
            return 50.0

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

    def get_budget_status(self) -> dict:
        """Return full budget status with threshold alerts."""
        if not self.is_allocated:
            if not self.is_setup:
                return {"status": "error", "message": "No trip set up yet. Use setup_trip first."}
            return {"status": "error", "message": "Budget not allocated yet. Use allocate_budget first."}

        categories = {}
        total_spent = 0
        total_budget = self.trip["total_budget"]

        for cat in self.allocation:
            budget = self.allocation[cat]
            spent = self.spent[cat]
            remaining = budget - spent
            pct = (spent / budget * 100) if budget > 0 else 0
            total_spent += spent

            categories[cat] = {
                "budget": round(budget, 2),
                "spent": round(spent, 2),
                "remaining": round(remaining, 2),
                "percent_used": round(pct, 1),
                "status": "over_budget" if remaining < 0 else
                          "critical" if pct >= 85 else
                          "warning" if pct >= 70 else "ok"
            }

        alerts = self._check_thresholds()
        trip_progress = self._trip_progress_percent()

        return {
            "status": "success",
            "trip": self.trip,
            "categories": categories,
            "overall": {
                "total_budget": round(total_budget, 2),
                "total_spent": round(total_spent, 2),
                "total_remaining": round(total_budget - total_spent, 2),
                "percent_used": round((total_spent / total_budget * 100) if total_budget > 0 else 0, 1)
            },
            "trip_progress_percent": trip_progress,
            "expense_count": len(self.expenses),
            "alerts": alerts,
            "currency": self.trip["home_currency"]
        }