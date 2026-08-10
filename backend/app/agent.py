import json
from typing import AsyncGenerator

from .tools import search_places, get_directions, get_place_details
from .memory import get_memory


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_places",
            "description": "Search for places matching a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "location": {"type": "string", "description": "Optional location context"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_directions",
            "description": "Get directions between two locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "mode": {"type": "string", "enum": ["driving", "walking", "transit"]}
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_place_details",
            "description": "Get detailed info about a specific place",
            "parameters": {
                "type": "object",
                "properties": {
                    "place_id": {"type": "string"}
                },
                "required": ["place_id"]
            }
        }
    },
]

TOOL_MAP = {
    "search_places": search_places,
    "get_directions": get_directions,
    "get_place_details": get_place_details,
}


async def run_agent(user_message: str, session_id: str = "default") -> AsyncGenerator[dict, None]:
    memory = get_memory(session_id)
    memory.add_message("user", user_message)

    messages = [{"role": "system", "content": "You are a route planner AI assistant. Help users plan trips, find places, and get directions."}]
    messages.extend(memory.get_history())

    # Simulate agent loop with tool calls
    response_text = f"I'll help you plan your route. Let me search for information about: {user_message}"
    tool_trace = []

    # Execute tools based on keywords
    if any(word in user_message.lower() for word in ["find", "search", "places"]):
        result = await search_places(user_message)
        tool_trace.append({"tool": "search_places", "args": {"query": user_message}, "result": result})
        response_text += f"\n\nI found some places for you: {json.dumps(result[:2] if isinstance(result, list) else result, indent=2)}"

    if any(word in user_message.lower() for word in ["direction", "route", "how to"]):
        result = await get_directions("origin", "destination")
        tool_trace.append({"tool": "get_directions", "args": {"origin": "origin", "destination": "destination"}, "result": result})
        response_text += "\n\nI've calculated the route for you."

    if not tool_trace:
        response_text = f"I understand you're asking about: {user_message}. I can help you search for places, get directions, or find details about specific locations. What would you like to know?"

    memory.add_message("assistant", response_text, tool_trace)

    yield {"type": "trace", "tools_called": tool_trace}
    yield {"type": "response", "content": response_text}
