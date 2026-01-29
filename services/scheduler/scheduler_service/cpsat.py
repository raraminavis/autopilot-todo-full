from __future__ import annotations

"""
CP-SAT scheduling scaffold.

This file intentionally contains:
- data transforms you will keep
- hook points for constraints/objective
- a placeholder 'not implemented' solve, so you can progressively add features

When you're ready, implement:
- free windows -> candidate starts
- plan selection vars y[t,p]
- optional interval vars for chunks
- NoOverlap + precedence constraints
- objective terms: deadline risk, switching, energy fit, split penalty, minimal-change
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

from ortools.sat.python import cp_model

from .schemas import TaskIn, ProposedBlock
from .plan_generator import SplitPolicy, generate_plans

@dataclass
class SolverConfig:
    slot_minutes: int = 15
    max_seconds: int = 3

def solve_with_cpsat(tasks: list[TaskIn], now: datetime, cfg: SolverConfig) -> list[ProposedBlock]:
    model = cp_model.CpModel()

    # Example: build plans per task (the key idea for upfront splitting)
    task_plans: dict[str, list[list[int]]] = {}
    for t in tasks:
        pol = SplitPolicy(
            splittable=t.splittable,
            min_chunk=t.min_chunk_minutes,
            preferred_chunk=t.preferred_chunk_minutes,
            max_chunk=t.max_chunk_minutes,
            max_chunks=t.max_chunks,
        )
        task_plans[t.task_id] = generate_plans(t.estimated_minutes, pol)

    # TODO: turn free windows into discrete slots and candidate starts
    # TODO: create y[t,p] plan selection variables and optional interval vars
    # TODO: add NoOverlap constraints + due constraints + occupiedness constraints
    # TODO: objective: split penalty, deadline risk, energy fit, switching, minimal-change

    # Placeholder: we return a deterministic "first feasible" layout from plans
    blocks: list[ProposedBlock] = []
    cursor = now.replace(minute=(now.minute // cfg.slot_minutes) * cfg.slot_minutes, second=0, microsecond=0)
    for t in tasks:
        plans = task_plans[t.task_id]
        plan = plans[0]  # fewest chunks (likely [total])
        chunk_group_id = f"cg_{uuid.uuid4().hex[:8]}"
        for i, minutes in enumerate(plan):
            start = cursor
            end = start + timedelta(minutes=minutes)
            blocks.append(
                ProposedBlock(
                    task_id=t.task_id,
                    start_at=start.isoformat(),
                    end_at=end.isoformat(),
                    chunk_group_id=chunk_group_id,
                    chunk_index=i,
                    chunk_count=len(plan),
                    explain_tags=["cpsat_scaffold_plan_first"],
                )
            )
            cursor = end
    return blocks
