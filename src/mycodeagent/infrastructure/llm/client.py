"""LLM统一客户端"""

import os
import time
from dataclasses import dataclass
from typing import Any

from ...agents.base import LLMMessage


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict[str, int] | None = None


class BaseLLMClient:
    async def chat(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        raise NotImplementedError


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def chat(self, messages: list[LLMMessage], model: str | None = None, temperature: float = 0.7, **kwargs) -> LLMResponse:
        if not self.api_key:
            raise ValueError("OpenAI API key未设置")

        client = self._get_client()
        openai_messages = [{"role": m.role, "content": m.content} for m in messages]

        response = await client.chat.completions.create(
            model=model or self.model,
            messages=openai_messages,
            temperature=temperature,
            **kwargs
        )

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=model or self.model,
            usage={"total_tokens": response.usage.total_tokens} if response.usage else None
        )


class UnifiedLLMClient:
    """统一LLM客户端"""

    def __init__(self, default_provider: str = "openai"):
        self._providers: dict[str, BaseLLMClient] = {}
        self._default_provider = default_provider

    def register_provider(self, name: str, provider: BaseLLMClient) -> None:
        self._providers[name] = provider

    async def chat(self, messages: list[LLMMessage], provider: str | None = None, **kwargs) -> LLMResponse:
        provider_name = provider or self._default_provider
        provider_client = self._providers.get(provider_name)
        if not provider_client:
            raise ValueError(f"Provider不存在: {provider_name}")
        return await provider_client.chat(messages, **kwargs)
