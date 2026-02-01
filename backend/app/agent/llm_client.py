from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence, Union

from spoon_ai.llm import ConfigurationManager, LLMManager
from spoon_ai.schema import Message


MessageLike = Union[Message, Dict[str, str]]


class LLMClient:
    def __init__(self, providers: Optional[List[str]] = None) -> None:
        self.providers = providers or ["gemini"]
        self._manager = LLMManager(ConfigurationManager())

    async def chat_json(
        self,
        messages: Sequence[MessageLike],
        fallback: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        formatted = _to_messages(messages)
        last_payload: Optional[Dict[str, Any]] = None

        for provider in self.providers:
            try:
                response = await self._manager.chat(messages=formatted, provider=provider)
                content = getattr(response, "content", "") or ""
                payload = _extract_json(content)
                if payload is None:
                    last_payload = None
                    continue
                return payload
            except Exception:
                continue

        return last_payload or fallback or {}


def _to_messages(messages: Sequence[MessageLike]) -> List[Message]:
    formatted: List[Message] = []
    for item in messages:
        if isinstance(item, Message):
            formatted.append(item)
            continue
        role = item.get("role") if isinstance(item, dict) else None
        content = item.get("content") if isinstance(item, dict) else None
        if role is None:
            role = "user"
        formatted.append(Message(role=role, content=content))
    return formatted


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
