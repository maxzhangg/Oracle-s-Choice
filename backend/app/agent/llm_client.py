from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Sequence, Union

from spoon_ai.llm import ConfigurationManager, LLMManager
from spoon_ai.schema import Message


MessageLike = Union[Message, Dict[str, str]]

PROVIDER_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


class LLMClient:
    def __init__(self, providers: Optional[List[str]] = None) -> None:
        ordered = providers or ["deepseek"]
        self.providers = _filter_providers(ordered)
        self._manager = LLMManager(ConfigurationManager())

    async def chat_json(
        self,
        messages: Sequence[MessageLike],
        fallback: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        formatted = _to_messages(messages)
        last_payload: Optional[Dict[str, Any]] = None

        for provider in self.providers:
            retries = _get_retries()
            for _ in range(retries + 1):
                try:
                    response = await self._manager.chat(
                        messages=formatted,
                        provider=provider,
                        **_provider_kwargs(provider),
                    )
                    content = getattr(response, "content", "") or ""
                    payload = _extract_json(content)
                    if payload is None:
                        if content:
                            return {"_provider": provider, "_raw": content}
                        last_payload = None
                        continue
                    if isinstance(payload, dict):
                        payload["_provider"] = provider
                    return payload
                except Exception:
                    continue

        return last_payload or fallback or {}


def _filter_providers(providers: List[str]) -> List[str]:
    available: List[str] = []
    for provider in providers:
        key_name = PROVIDER_KEYS.get(provider)
        if not key_name:
            available.append(provider)
            continue
        if os.getenv(key_name):
            available.append(provider)
    return available


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


def _provider_kwargs(provider: str) -> Dict[str, Any]:
    max_tokens = _get_max_tokens()
    if provider == "deepseek":
        return {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "max_tokens": max_tokens,
        }
    return {"max_tokens": max_tokens}


def _get_max_tokens() -> int:
    raw = os.getenv("LLM_MAX_TOKENS", "512")
    try:
        value = int(raw)
    except ValueError:
        value = 512
    return min(max(value, 1), 8192)


def _get_retries() -> int:
    raw = os.getenv("LLM_RETRIES", "1")
    try:
        value = int(raw)
    except ValueError:
        value = 1
    return max(value, 0)
