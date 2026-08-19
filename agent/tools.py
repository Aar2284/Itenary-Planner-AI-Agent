"""Tool Implementations - dispatch agent tool calls to handlers."""

import json
import requests
from agent.state import TripState


def execute_tool(tool_name: str, arguments: dict, state: TripState) -> str:
    """Dispatch a tool call to the correct implementation."""
    handlers = {
        "setup_trip": _handle_setup_trip,
        "allocate_budget": _handle_allocate_budget,
        "get_exchange_rate": _handle_get_exchange_rate,
        "log_expense": _handle_log_expense,
        "get_budget_status": _handle_get_budget_status,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return json.dumps({"status": "error", "message": f"Unknown tool: {tool_name}"})

    try:
        result = handler(arguments, state)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Tool execution failed: {str(e)}"})

def _handle_setup_trip(args: dict, state: TripState) -> dict:
    """Initialize trip parameters."""
    return state.setup_trip(
        destination=args["destination"],
        home_currency=args["home_currency"],
        local_currency=args["local_currency"],
        start_date=args["start_date"],
        end_date=args["end_date"],
        total_budget=args["total_budget"]
    )


def _handle_allocate_budget(args: dict, state: TripState) -> dict:
    """Split budget across categories."""
    return state.allocate_budget(
        lodging=args["lodging"],
        food=args["food"],
        transport=args["transport"],
        activities=args["activities"],
        shopping=args["shopping"]
    )

def _handle_get_exchange_rate(args: dict, state: TripState) -> dict:
    """Call the Frankfurter API for live FX rates."""
    base = args["base_currency"].upper()
    target = args["target_currency"].upper()

    try:
        url = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={target}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        rate = data["rates"].get(target)
        if rate is None:
            return {
                "status": "error",
                "message": f"Could not find rate for {base} -> {target}"
            }

        return {
            "status": "success",
            "base_currency": base,
            "target_currency": target,
            "rate": rate,
            "date": data.get("date", "unknown"),
            "message": f"1 {base} = {rate} {target}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to fetch exchange rate: {str(e)}"
        }