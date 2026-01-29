from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    ok: bool = True

class TaskCaptureRequest(BaseModel):
    text: str = Field(min_length=1)
    client_timestamp: datetime

class TaskOut(BaseModel):
    task_id: str
    raw_text: str
    due_type: str
    due_at: datetime | None = None
    due_window_start: datetime | None = None
    due_window_end: datetime | None = None
    estimated_minutes: int
    status: str

class TaskCaptureResponse(BaseModel):
    task: TaskOut
    needs_clarification: bool = False
    clarification_question: str | None = None

class ScheduleProposeRequest(BaseModel):
    horizon_days: int = 7
    trigger: str = "manual"
    strategy: str = "AUTO"

class ProposedBlock(BaseModel):
    task_id: str
    start_at: datetime
    end_at: datetime
    chunk_group_id: str | None = None
    chunk_index: int | None = None
    chunk_count: int | None = None
    explain_tags: list[str] = []

class ScheduleProposeResponse(BaseModel):
    proposal_id: str
    requires_confirmation: bool
    proposed_blocks: list[ProposedBlock]
    alternatives: list[str] = []

class MarkUnfinishedRequest(BaseModel):
    remaining_minutes: int = Field(ge=1)
