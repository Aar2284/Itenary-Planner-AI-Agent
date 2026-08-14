"""
The agent: a plan-act loop built on Groq's function/tool calling.

How this satisfies "agent, not chatbot" from the assignment:
- The LLM is given tool *descriptions*, not answers. It decides for
  itself which tool to call, with what arguments, and whether it has
  enough information yet to call order_stops at all.
- Each tool result is fed back to the model, which then decides the
  NEXT step -- that's "more than one step, deciding what to do next
  from tool results," implemented literally as the while-loop below.
- memory.TripContext.summary() is injected into the system prompt on
  every single call, so decisions are grounded in what actually
  happened earlier in the conversation.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

from app.tools import get_distance, order_stops
from app.memory import TripContext

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
MAX_LOOP_STEPS = 8  # safety cap so a confused model can't loop forever

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_distance",
            "description": (
                "Get the real road distance (km) and driving time (minutes) "
                "between two named places. Call this for each pair of places "
                "you need distance information for, BEFORE calling order_stops."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "string", "description": "First place name"},
                    "b": {"type": "string", "description": "Second place name"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "order_stops",
            "description": (
                "Compute a sensible visiting order for a list of stops using "
                "a nearest-neighbor route over real road distances. Only call "
                "this once you know which stops need to be routed -- typically "
                "after using get_distance to understand the layout, or when "
                "the user asks you to (re)plan the route."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "stops": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of place names to visit, in any order",
                    },
                    "start": {
                        "type": "string",
                        "description": "Optional fixed starting place",
                    },
                },
                "required": ["stops"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "get_distance": get_distance,
    "order_stops": order_stops,
}


def build_system_prompt(memory: TripContext) -> str:
    """
    Rebuilt every turn so it always reflects the CURRENT memory state
    -- this is how "memory read back into a later decision" actually
    happens mechanically.
    """
    return f"""You are a multi-stop route planning agent.

Your job: given places the user wants to visit, work out a sensible
visiting order, not just repeat the order they were mentioned in.

Rules you must follow:
1. Before calling order_stops for the first time, call get_distance
   for at least a few relevant pairs so you understand the layout.
2. Never include a place in a route that the user has marked as
   already visited.
3. If the user adds a new stop or marks one as visited after a route
   was already computed, recompute the route with order_stops rather
   than editing the old route by hand.
4. Always explain your reasoning briefly when you present a route
   (e.g. why this order, what the total distance/time is).
5. If a place isn't found, tell the user plainly instead of guessing
   coordinates or distances yourself.

Current memory (what you already know from this conversation):
{memory.summary()}
"""


def run_agent_turn(user_message: str, memory: TripContext, verbose: bool = True) -> dict:
    """
    Runs one full plan-act loop for a single user message: calls the
    model, executes any tool calls it requests, feeds results back,
    and repeats until the model produces a final text answer.

    Returns {"reply": final text, "trace": list of tool-call steps}.
    `memory` is mutated in place so the caller's TripContext stays in
    sync across turns.
    """
    messages = [
        {"role": "system", "content": build_system_prompt(memory)},
        {"role": "user", "content": user_message},
    ]
    trace = []

    for step in range(MAX_LOOP_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            if verbose:
                print(f"[step {step}] final answer:\n{msg.content}\n")
            return {"reply": msg.content, "trace": trace}

        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if verbose:
                print(f"[step {step}] tool call: {name}({args})")

            result = TOOL_FUNCTIONS[name](**args)

            if name == "order_stops" and "route" in result:
                memory.set_route(
                    result["route"],
                    result["total_distance_km"],
                    result.get("total_duration_min"),
                )

            if verbose:
                print(f"[step {step}] tool result: {result}\n")

            trace.append({
                "step": step,
                "tool": name,
                "arguments": args,
                "result": result,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

    return {
        "reply": "Agent stopped: reached max steps without a final answer.",
        "trace": trace,
    }