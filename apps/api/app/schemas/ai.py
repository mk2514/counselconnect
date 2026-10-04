from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIOutputResponse(BaseModel):
    id: UUID
    ai_job_id: UUID
    output_type: str
    content: str
    model_metadata: dict[str, Any] | None
    created_at: datetime
    verified_by: UUID | None
    verified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AIJobResponse(BaseModel):
    id: UUID
    case_id: UUID | None
    document_id: UUID | None = None
    job_type: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    error_message: str | None
    outputs: list[AIOutputResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SummarizeRequest(BaseModel):
    case_id: UUID
