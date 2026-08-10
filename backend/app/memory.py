from typing import Optional


class ConversationMemory:
    def __init__(self):
        self.history: list[dict] = []
        self.user_preferences: dict = {}

    def add_message(self, role: str, content: str, tool_calls: Optional[list] = None):
        entry = {"role": role, "content": content}
        if tool_calls:
            entry["tool_calls"] = tool_calls
        self.history.append(entry)

    def get_history(self) -> list[dict]:
        return self.history

    def set_preference(self, key: str, value: str):
        self.user_preferences[key] = value

    def get_preferences(self) -> dict:
        return self.user_preferences

    def clear(self):
        self.history.clear()
        self.user_preferences.clear()


memory_store: dict[str, ConversationMemory] = {}


def get_memory(session_id: str) -> ConversationMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ConversationMemory()
    return memory_store[session_id]
