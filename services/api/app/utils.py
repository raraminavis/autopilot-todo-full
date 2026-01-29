from __future__ import annotations

import re
from datetime import datetime, timedelta

def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def default_soft_window(now: datetime, days: int = 3) -> tuple[datetime, datetime]:
    end = (now + timedelta(days=days)).replace(hour=23, minute=59, second=0, microsecond=0)
    return now, end
