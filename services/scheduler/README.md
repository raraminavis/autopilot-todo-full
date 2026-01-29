# services/scheduler

Scheduling engine service.

## Endpoint
- `POST /v1/solve` — takes tasks + free windows and returns proposed blocks.

This scaffold returns a **valid structure** and includes:
- plan-based chunk plan generation (`plans`)
- a CP-SAT model skeleton (hook points)
- a greedy fallback (so you can run end-to-end now)

## Run
```bash
pip install -e ".[dev]"
uvicorn scheduler_service.main:app --reload --port 8001
```
