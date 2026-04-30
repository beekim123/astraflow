from pydantic import BaseModel


class AgentRequest(BaseModel):
    task_type: str
    user_id: str
    payload: dict


class AgentResult(BaseModel):
    task_type: str
    status: str
    summary: str
    data: dict = {}

