from __future__ import annotations

import uuid
from sqlalchemy.orm import Session
from .models import EventLog

def log_event(db: Session, user_id: str, event_type: str, payload: dict) -> str:
    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    db.add(EventLog(event_id=event_id, user_id=user_id, event_type=event_type, payload=payload))
    db.commit()
    return event_id
