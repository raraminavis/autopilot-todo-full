from __future__ import annotations

import uuid
from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from .models import User
from .events import log_event

def get_user_id(x_user_id: str | None = Header(default=None)) -> str:
    # local-dev auth: pass X-User-Id. If absent, use a stable demo user.
    return x_user_id or "u_demo"

def ensure_user(db: Session, user_id: str) -> None:
    u = db.get(User, user_id)
    if u is None:
        db.add(User(user_id=user_id))
        db.commit()
        log_event(db, user_id, "UserCreated", {"user_id": user_id})
