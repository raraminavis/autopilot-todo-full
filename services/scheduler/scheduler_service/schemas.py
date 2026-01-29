from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any

class TaskIn(BaseModel):
    task_id: str
    estimated_minutes: int = Field(ge=1)
    due_type: str
    due_at: str | None = None
    due_window_start: str | None = None
    due_window_end: str | None = None

    splittable: bool = True
    min_chunk_minutes: int = 30
    preferred_chunk_minutes: int = 60
    max_chunk_minutes: int = 120
    max_chunks: int = 4
    split_penalty_weight: float = 1.0

class SolveRequest(BaseModel):
    user_id: str
    horizon_days: int = 7
    strategy: str = "AUTO"
    timezone: str = "America/New_York"
    tasks: list[TaskIn]
    free_windows: list[dict] = []  # full product: list of {start_at,end_at} iso

class ProposedBlock(BaseModel):
    task_id: str
    start_at: str
    end_at: str
    chunk_group_id: str | None = None
    chunk_index: int | None = None
    chunk_count: int | None = None
    explain_tags: list[str] = []

class SolveResponse(BaseModel):
    strategy: str
    objective_weights: dict
    diff: dict
    proposed_blocks: list[ProposedBlock]
    alternatives: list[str] = []
    debug: dict = {}
