from __future__ import annotations

from .celery_app import celery_app

@celery_app.task(name="worker.tasks.sync_calendar")
def sync_calendar(user_id: str) -> dict:
    # TODO: use Google sync tokens to update calendar cache and detect conflicts.
    return {"ok": True, "user_id": user_id}

@celery_app.task(name="worker.tasks.replan_user")
def replan_user(user_id: str, reason: str = "manual") -> dict:
    # TODO: trigger scheduler propose/apply flow depending on autonomy mode.
    return {"ok": True, "user_id": user_id, "reason": reason}
