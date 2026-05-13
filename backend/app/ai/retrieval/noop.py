from time import perf_counter

from app.ai.retrieval.base import Retriever
from app.ai.retrieval.schemas import RetrievalQuery, RetrievalResult


class NoopRetriever(Retriever):
    async def search(self, query: RetrievalQuery) -> RetrievalResult:
        started = perf_counter()
        return RetrievalResult(
            query=query.query,
            evidence=[],
            rewritten_query=query.query,
            latency_ms=int((perf_counter() - started) * 1000),
        )
