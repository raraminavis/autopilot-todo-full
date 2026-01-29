from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from .schemas import SolveRequest, SolveResponse
from .greedy import greedy_schedule
from .cpsat import solve_with_cpsat, SolverConfig

app = FastAPI(title="Autopilot Scheduler", version="0.1.0")

@app.get("/v1/health")
def health():
    return {"ok": True}

@app.post("/v1/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    now = datetime.now(timezone.utc).astimezone(timezone.utc)

    # Strategy selection placeholder
    strategy = "A_deadline" if req.strategy in ("AUTO", "A_deadline") else req.strategy

    # Use CP-SAT scaffold by default, greedy if empty tasks
    if not req.tasks:
        blocks = []
    else:
        cfg = SolverConfig(slot_minutes=15, max_seconds=3)
        blocks = solve_with_cpsat(req.tasks, now=now, cfg=cfg)

    return SolveResponse(
        strategy=strategy,
        objective_weights={"w_deadline": 10, "w_split": 1},
        diff={},
        proposed_blocks=blocks,
        alternatives=[],
        debug={"note": "CP-SAT scaffold returns plan-first sequential layout until constraints wired."},
    )
