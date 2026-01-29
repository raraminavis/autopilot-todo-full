from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from .schemas import TaskIn, ProposedBlock

def greedy_schedule(tasks: list[TaskIn], now: datetime, slot_minutes: int = 15) -> list[ProposedBlock]:
    """
    Fallback planner: schedules chunks back-to-back starting 'now' in slot increments.
    This is ONLY for end-to-end smoke tests until free windows + CP-SAT are wired.
    """
    blocks: list[ProposedBlock] = []
    cursor = now.replace(minute=(now.minute // slot_minutes) * slot_minutes, second=0, microsecond=0)
    for t in tasks:
        chunk_group_id = f"cg_{uuid.uuid4().hex[:8]}"
        # naive: one chunk (full product will choose plans)
        minutes = t.estimated_minutes
        end = cursor + timedelta(minutes=minutes)
        blocks.append(
            ProposedBlock(
                task_id=t.task_id,
                start_at=cursor.isoformat(),
                end_at=end.isoformat(),
                chunk_group_id=chunk_group_id,
                chunk_index=0,
                chunk_count=1,
                explain_tags=["greedy_fallback"],
            )
        )
        cursor = end
    return blocks
