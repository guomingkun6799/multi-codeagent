"""Agent基类模块"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Agent执行结果"""
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, data: dict[str, Any] = None, **kwargs) -> "AgentResult":
        return cls(success=True, data=data or kwargs)

    @classmethod
    def fail(cls, error: str, **kwargs) -> "AgentResult":
        return cls(success=False, error=error, metadata=kwargs)


@dataclass
class LLMMessage:
    """LLM消息"""
    role: str  # system, user, assistant
    content: str


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, llm_client: Any = None) -> None:
        self._llm = llm_client

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def description(self) -> str:
        return f"{self.name} Agent"

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        pass

    async def chat_with_llm(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        if self._llm is None:
            raise RuntimeError(f"Agent {self.name} 未配置LLM客户端")

        response = await self._llm.chat(
            messages=messages,
            agent_name=self.name,
            temperature=temperature,
            **kwargs
        )
        return response.content
