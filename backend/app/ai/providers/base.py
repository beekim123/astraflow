from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.ai.contracts.schemas import AgentRequest, AgentResult, AgentStreamChunk


class AiProvider(ABC):
    provider_name = "base"

    @abstractmethod
    async def run(self, request: AgentRequest, prompt: str) -> AgentResult:
        """Execute one AI request and return a normalized result."""

    async def stream(self, request: AgentRequest, prompt: str) -> AsyncIterator[AgentStreamChunk]:
        result = await self.run(request, prompt)
        if result.reasoning_summary:
            yield AgentStreamChunk(type="reasoning_delta", content=result.reasoning_summary)
        for char in result.summary:
            yield AgentStreamChunk(type="answer_delta", content=char)
        yield AgentStreamChunk(type="provider_done", data=result.model_dump())
