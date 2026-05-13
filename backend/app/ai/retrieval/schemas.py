from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    user_id: str
    conversation_id: str | None = None
    query: str
    top_k: int = 5
    filters: dict = Field(default_factory=dict)


class Evidence(BaseModel):
    source_id: str = ""
    source_type: str = ""
    title: str = ""
    snippet: str = ""
    score: float = 0
    metadata: dict = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    query: str
    evidence: list[Evidence] = Field(default_factory=list)
    rewritten_query: str = ""
    latency_ms: int = 0
