from __future__ import annotations
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/integrations/google/calendar/webhook")
async def calendar_webhook(request: Request):
    # TODO: verify headers, enqueue sync job, refresh cache, detect conflicts, replan.
    return {"ok": True}
