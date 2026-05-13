from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.ai.contracts.schemas import AgentRequest, AgentResult


class AgentClient(ABC):
    @abstractmethod
    async def run(self, request: AgentRequest) -> AgentResult:
        """Run an AI task behind a stable boundary."""

    @abstractmethod
    async def stream(self, request: AgentRequest) -> AsyncIterator[dict]:
        """Stream normalized AI events behind a stable boundary."""
