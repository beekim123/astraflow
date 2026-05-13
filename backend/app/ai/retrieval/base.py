from abc import ABC, abstractmethod

from app.ai.retrieval.schemas import RetrievalQuery, RetrievalResult


class Retriever(ABC):
    @abstractmethod
    async def search(self, query: RetrievalQuery) -> RetrievalResult:
        """Search knowledge sources and return evidence for prompt injection."""
