from __future__ import annotations

import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "autopilot_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.task_routes = {
    "worker.tasks.sync_calendar": {"queue": "sync"},
    "worker.tasks.replan_user": {"queue": "replan"},
}
