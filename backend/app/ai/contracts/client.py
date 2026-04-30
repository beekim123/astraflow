from abc import ABC, abstractmethod

from app.ai.contracts.schemas import AgentRequest, AgentResult


class AgentClient(ABC):
    @abstractmethod
    async def run(self, request: AgentRequest) -> AgentResult:
        """Run an AI task behind a stable boundary."""

