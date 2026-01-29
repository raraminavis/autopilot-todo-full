from __future__ import annotations

from datetime import datetime
import httpx
from ..config import settings

async def propose_schedule(payload: dict) -> dict:
    url = f"{settings.scheduler_url}/v1/solve"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()
