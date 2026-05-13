from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    task_type: str
    user_id: str
    payload: dict = Field(default_factory=dict)
    mode: str = "mock"
    model: str = ""
    temperature: int = 70
    max_tokens: int = 2048
    prompt_scene: str = "chat-general"
    conversation_id: str | None = None
    message_id: str | None = None
    request_id: str = ""


class AgentResult(BaseModel):
    task_type: str
    status: str
    summary: str
    data: dict = Field(default_factory=dict)
    provider: str = "mock"
    model: str = "mock-assistant"
    mode: str = "mock"
    prompt_version: str = "v1"
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: int = 0
    fallback_used: bool = False
    reasoning_summary: str = ""
    process_steps: list[str] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    route_chain: list[dict] = Field(default_factory=list)


class AgentStreamChunk(BaseModel):
    type: str
    content: str = ""
    data: dict = Field(default_factory=dict)
