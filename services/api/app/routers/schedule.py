from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_user_id, ensure_user
from ..schemas import ScheduleProposeRequest, ScheduleProposeResponse, ProposedBlock, MarkUnfinishedRequest
from ..models import Task, ScheduleProposal, ProposalAction, TaskInstance
from ..events import log_event
from ..clients.scheduler_client import propose_schedule

router = APIRouter()

@router.post("/schedule/propose", response_model=ScheduleProposeResponse)
async def schedule_propose(
    req: ScheduleProposeRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    ensure_user(db, user_id)

    # Fetch unassigned tasks for now (full product will include impacted tasks)
    tasks = db.query(Task).filter(Task.user_id == user_id, Task.status == "unassigned").all()

    payload = {
        "user_id": user_id,
        "horizon_days": req.horizon_days,
        "strategy": req.strategy,
        "tasks": [
            {
                "task_id": t.task_id,
                "estimated_minutes": t.estimated_minutes,
                "due_type": t.due_type,
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "due_window_start": t.due_window_start.isoformat() if t.due_window_start else None,
                "due_window_end": t.due_window_end.isoformat() if t.due_window_end else None,
                "splittable": t.splittable,
                "min_chunk_minutes": t.min_chunk_minutes,
                "preferred_chunk_minutes": t.preferred_chunk_minutes,
                "max_chunk_minutes": t.max_chunk_minutes,
                "max_chunks": t.max_chunks,
                "split_penalty_weight": t.split_penalty_weight,
            }
            for t in tasks
        ],
        # In full product: include calendar free windows computed from Google cache
        "free_windows": [],
        "timezone": "America/New_York",
    }

    result = await propose_schedule(payload)

    proposal_id = f"p_{uuid.uuid4().hex[:12]}"
    proposal = ScheduleProposal(
        proposal_id=proposal_id,
        user_id=user_id,
        strategy=result.get("strategy", "A_deadline"),
        objective_weights=result.get("objective_weights", {}),
        diff=result.get("diff", {}),
        requires_confirmation=True,
        status="pending",
    )
    db.add(proposal)
    db.commit()

    log_event(db, user_id, "ScheduleProposed", {"proposal_id": proposal_id})

    blocks = []
    for b in result.get("proposed_blocks", []):
        blocks.append(
            ProposedBlock(
                task_id=b["task_id"],
                start_at=datetime.fromisoformat(b["start_at"]),
                end_at=datetime.fromisoformat(b["end_at"]),
                chunk_group_id=b.get("chunk_group_id"),
                chunk_index=b.get("chunk_index"),
                chunk_count=b.get("chunk_count"),
                explain_tags=b.get("explain_tags", []),
            )
        )

    return ScheduleProposeResponse(
        proposal_id=proposal_id,
        requires_confirmation=True,
        proposed_blocks=blocks,
        alternatives=result.get("alternatives", []),
    )

@router.post("/schedule/proposals/{proposal_id}/accept")
def schedule_accept(
    proposal_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    ensure_user(db, user_id)

    # NOTE: In a full product, we'd store proposed blocks in DB and apply them.
    # For scaffold, we simply record the action.
    action = ProposalAction(
        action_id=f"a_{uuid.uuid4().hex[:12]}",
        proposal_id=proposal_id,
        user_id=user_id,
        action_type="accept",
        action_payload={"proposal_id": proposal_id},
    )
    db.add(action)
    db.commit()
    log_event(db, user_id, "ProposalAccepted", {"proposal_id": proposal_id})
    return {"applied": True}

@router.post("/task_instances/{task_instance_id}/mark_unfinished")
def mark_unfinished(
    task_instance_id: str,
    req: MarkUnfinishedRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    ensure_user(db, user_id)
    ti = db.get(TaskInstance, task_instance_id)
    if not ti:
        return {"error": "not_found"}

    ti.completion_state = "user_marked_unfinished"
    ti.remaining_minutes = req.remaining_minutes
    db.commit()
    log_event(db, user_id, "TaskMarkedUnfinished", {"task_instance_id": task_instance_id, "remaining": req.remaining_minutes})
    return {"ok": True}
