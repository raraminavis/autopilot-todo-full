from __future__ import annotations

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_user_id, ensure_user
from ..schemas import TaskCaptureRequest, TaskCaptureResponse, TaskOut
from ..models import Task
from ..utils import normalize_text, default_soft_window
from ..events import log_event

router = APIRouter()

@router.post("/tasks/capture", response_model=TaskCaptureResponse)
def capture_task(req: TaskCaptureRequest, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    ensure_user(db, user_id)

    normalized = normalize_text(req.text)
    # TODO: plug in real temporal parsing & feature inference (see docs/INFERENCE_SPEC.md)
    due_type = "soft_window"
    ws, we = default_soft_window(req.client_timestamp)

    task_id = f"t_{uuid.uuid4().hex[:12]}"
    task = Task(
        task_id=task_id,
        user_id=user_id,
        raw_text=req.text,
        normalized_text=normalized,
        due_type=due_type,
        due_window_start=ws,
        due_window_end=we,
        estimated_minutes=30,
        status="unassigned",
    )
    db.add(task)
    db.commit()

    log_event(db, user_id, "TaskCaptured", {"task_id": task_id, "text": req.text})

    return TaskCaptureResponse(
        task=TaskOut(
            task_id=task.task_id,
            raw_text=task.raw_text,
            due_type=task.due_type,
            due_at=task.due_at,
            due_window_start=task.due_window_start,
            due_window_end=task.due_window_end,
            estimated_minutes=task.estimated_minutes,
            status=task.status,
        ),
        needs_clarification=False,
    )
