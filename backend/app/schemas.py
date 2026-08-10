from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ToolCall(BaseModel):
    tool: str
    args: dict
    result: dict


class ChatResponse(BaseModel):
    response: str
    trace: list[ToolCall] = []
