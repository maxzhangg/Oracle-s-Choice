from __future__ import annotations

import asyncio
import os

from spoon_ai.llm import ConfigurationManager, LLMManager
from spoon_ai.schema import Message


async def run_chat(llm: LLMManager) -> None:
    model = os.getenv("DEEPSEEK_CHAT_MODEL", os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    response = await llm.chat(
        messages=[Message(role="user", content="Say hello in Chinese.")],
        provider="deepseek",
        model=model,
        max_tokens=512,
    )
    print("[chat] model=", model)
    print("[chat] response=", response.content)


async def run_reasoner(llm: LLMManager) -> None:
    model = os.getenv("DEEPSEEK_REASONER_MODEL", "deepseek-reasoner")
    response = await llm.chat(
        messages=[
            Message(
                role="user",
                content="Solve: If x+3=10, what is x? Explain briefly.",
            )
        ],
        provider="deepseek",
        model=model,
        max_tokens=512,
    )
    print("[reasoner] model=", model)
    print("[reasoner] response=", response.content)


async def main() -> None:
    config = ConfigurationManager()
    llm = LLMManager(config)

    if not os.getenv("DEEPSEEK_API_KEY"):
        raise SystemExit("DEEPSEEK_API_KEY is missing in environment.")

    print("DEEPSEEK_API_KEY: SET")
    await run_chat(llm)
    await run_reasoner(llm)


if __name__ == "__main__":
    asyncio.run(main())
