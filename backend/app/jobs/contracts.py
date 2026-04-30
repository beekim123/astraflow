from enum import StrEnum

from pydantic import BaseModel


class JobStatus(StrEnum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class JobMessage(BaseModel):
    job_id: str
    job_type: str
    payload: dict

