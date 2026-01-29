# services/api

FastAPI gateway.

## Auth (scaffold)
This scaffold uses `X-User-Id` header for simplicity in local dev.

## Endpoints
- `GET /v1/health`
- `POST /v1/tasks/capture`
- `POST /v1/schedule/propose`
- `POST /v1/schedule/proposals/{proposal_id}/accept`
- `POST /v1/task_instances/{task_instance_id}/mark_unfinished`
- `POST /v1/integrations/google/calendar/webhook` (stub)

## Run
```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
