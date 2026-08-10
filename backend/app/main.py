from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ChatRequest, ChatResponse
from .agent import run_agent

app = FastAPI(title="Route Planner AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    results = []
    async for event in run_agent(request.message, request.session_id):
        results.append(event)

    trace = next((r["tools_called"] for r in results if r["type"] == "trace"), [])
    response = next((r["content"] for r in results if r["type"] == "response"), "")

    return ChatResponse(response=response, trace=trace)
