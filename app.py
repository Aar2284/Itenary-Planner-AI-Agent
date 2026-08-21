"""
Trip Currency Budgeter — Flask Server
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

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

conversations: dict[str, list] = {}


def get_conversation(session_id: str) -> list:
    if session_id not in conversations:
        conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return conversations[session_id]


def run_agent_loop(session_id: str, user_message: str) -> str:
    state = get_or_create_session(session_id)
    history = get_conversation(session_id)
    history.append({"role": "user", "content": user_message})

    max_iterations = 10
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
            return f"Error calling Groq API: {str(e)}"

        message = response.choices[0].message

        if message.tool_calls:
            history.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    }
                    for tc in message.tool_calls
                ]
            })

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}

                result = execute_tool(func_name, func_args, state)
                history.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
            continue

        assistant_reply = message.content or "I'm not sure how to respond."
        history.append({"role": "assistant", "content": assistant_reply})

        if len(history) > 50:
            history[:] = [history[0]] + history[-40:]

        return assistant_reply

    return "I seem to be stuck in a loop. Could you try rephrasing?"