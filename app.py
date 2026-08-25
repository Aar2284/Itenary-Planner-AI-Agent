"""
Trip Currency Budgeter — Flask Server
--------------------------------------
This is the main orchestration layer. It:
1. Receives user messages via HTTP
2. Sends them to Groq with tool schemas
3. Executes any tool calls the LLM requests
4. Loops until the LLM produces a final text response
5. Returns the response to the frontend

This loop demonstrates "agent workflows and orchestration",
"autonomous execution pipelines", and "workflow chaining" from the syllabus.
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

from agent.prompts import SYSTEM_PROMPT, TOOL_SCHEMAS
from agent.tools import execute_tool
from agent.state import get_or_create_session, get_session

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model to use — Llama 3.3 70B with tool calling support
MODEL = "openai/gpt-oss-120b"

# Store conversation histories per session
conversations: dict[str, list] = {}


def get_conversation(session_id: str) -> list:
    """Get or initialize conversation history for a session."""
    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return conversations[session_id]


def run_agent_loop(session_id: str, user_message: str) -> str:
    """
    The core agent loop — this is the "orchestration" piece.

    Flow: user message → LLM reasoning → tool call(s) → execute → 
        feed result back → LLM reasons again → ... → final text response

    This loop continues until the LLM produces a response without tool calls,
    implementing "workflow chaining" and "autonomous execution pipelines".
    """
    state = get_or_create_session(session_id)
    if not get_session(session_id):
        # Re-register with the correct session_id
        from agent.state import _sessions
        state.session_id = session_id
        _sessions[session_id] = state

    history = get_conversation(session_id)
    history.append({"role": "user", "content": user_message})

    max_iterations = 10  # safety limit to prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=history,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                max_tokens=4096,
                temperature=0.7
            )
        except Exception as e:
            error_msg = f"Error calling Groq API: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg

        message = response.choices[0].message

        # If the LLM wants to call tool(s)
        if message.tool_calls:
            # Add the assistant's message (with tool calls) to history
            history.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # Execute each tool call and add results to history
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}

                print(f"[TOOL CALL] {func_name}({json.dumps(func_args, indent=2)})")

                result = execute_tool(func_name, func_args, state)
                print(f"[TOOL RESULT] {result[:200]}...")

                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Continue the loop — let the LLM process tool results
            continue

        # No tool calls — this is the final text response
        assistant_reply = message.content or "I'm not sure how to respond to that."
        history.append({"role": "assistant", "content": assistant_reply})

        # Trim history if it gets too long (keep system + last 40 messages)
        if len(history) > 50:
            history[:] = [history[0]] + history[-40:]

        return assistant_reply

    return "I seem to be stuck in a loop. Could you try rephrasing your request?"


# ── API Routes ───────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the chat UI."""
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    """Serve static assets."""
    return send_from_directory("static", path)


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    Expects: { "message": "...", "session_id": "..." }
    Returns: { "response": "...", "session_id": "..." }
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    session_id = data.get("session_id", "default")

    print(f"\n{'='*60}")
    print(f"[USER] {user_message}")
    print(f"[SESSION] {session_id}")

    response = run_agent_loop(session_id, user_message)

    print(f"[ASSISTANT] {response[:200]}...")
    print(f"{'='*60}\n")

    return jsonify({
        "response": response,
        "session_id": session_id
    })


@app.route("/api/status", methods=["GET"])
def status():
    """Get current trip status for a session."""
    session_id = request.args.get("session_id", "default")
    state = get_session(session_id)
    if not state:
        return jsonify({"status": "no_session"})

    if not state.is_setup:
        return jsonify({"status": "no_trip"})

    return jsonify(state.get_budget_status())


@app.route("/api/expenses", methods=["GET"])
def expenses():
    """Get expense history for a session."""
    session_id = request.args.get("session_id", "default")
    state = get_session(session_id)
    if not state:
        return jsonify({"expenses": []})

    return jsonify({"expenses": state.expenses})


@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset a session."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")

    if session_id in conversations:
        del conversations[session_id]

    from agent.state import _sessions
    if session_id in _sessions:
        del _sessions[session_id]

    return jsonify({"status": "reset", "message": "Session cleared."})


if __name__ == "__main__":
    print("\n[TripBudgetBuddy] Trip Currency Budgeter")
    print("=" * 50)
    print(f"Model: {MODEL}")
    print(f"Server: http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)
