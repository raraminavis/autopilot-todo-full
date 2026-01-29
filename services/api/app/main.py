from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import health, tasks, schedule, google_webhook

app = FastAPI(title="Autopilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(tasks.router, prefix="/v1", tags=["tasks"])
app.include_router(schedule.router, prefix="/v1", tags=["schedule"])
app.include_router(google_webhook.router, prefix="/v1", tags=["google"])

@app.get("/")
def root():
    return {"service": "autopilot-api", "ok": True}
