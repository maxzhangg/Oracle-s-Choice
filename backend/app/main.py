from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent.graph_agent import build_agent
from .storage.db import Storage


load_dotenv(override=True)

app = FastAPI(title="Oracle's Choice", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = Storage()
agent = build_agent(storage)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    force_divination: bool | None = None


class ChatResponse(BaseModel):
    session_id: str
    message: str
    tool: str
    trace: List[Dict[str, Any]]
    reading: Dict[str, Any]


TRACE_ORDER = ["parse", "route", "divination", "narration", "persist"]


def _normalize_trace(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    last_by_node: Dict[str, Dict[str, Any]] = {}
    for item in trace:
        node = item.get("node")
        if node:
            last_by_node[node] = item
    return [last_by_node[node] for node in TRACE_ORDER if node in last_by_node]


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    session_id = payload.session_id or str(uuid4())
    context = await agent.invoke(
        {
            "session_id": session_id,
            "question": payload.message,
            "force_divination": bool(payload.force_divination),
        }
    )

    reading = {
        "symbols": context.get("symbols", []),
        "verdict": context.get("verdict", ""),
        "advice": context.get("advice", []),
    }

    return ChatResponse(
        session_id=session_id,
        message=context.get("message", ""),
        tool=context.get("tool", ""),
        trace=_normalize_trace(context.get("trace", [])),
        reading=reading,
    )
