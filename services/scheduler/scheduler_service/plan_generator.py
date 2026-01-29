from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SplitPolicy:
    splittable: bool
    min_chunk: int
    preferred_chunk: int
    max_chunk: int
    max_chunks: int

def generate_plans(total_minutes: int, policy: SplitPolicy, max_plans: int = 8) -> list[list[int]]:
    """
    Plan-based chunking:
    Return a small menu of chunk-size lists that sum to total_minutes.

    Design goals:
    - include [total] when feasible (fewest chunks)
    - include [preferred,...] + remainder
    - include a more granular plan if needed
    - cap at max_plans
    """
    if not policy.splittable or policy.max_chunks <= 1:
        return [[total_minutes]]

    plans: list[list[int]] = []

    def add(plan: list[int]):
        if sum(plan) != total_minutes:
            return
        if any(c < policy.min_chunk or c > policy.max_chunk for c in plan):
            return
        if len(plan) > policy.max_chunks:
            return
        if plan not in plans:
            plans.append(plan)

    # 1) single block if allowed
    add([total_minutes])

    # 2) repeat preferred
    k = total_minutes // policy.preferred_chunk
    if k >= 1:
        base = [policy.preferred_chunk] * min(k, policy.max_chunks)
        remainder = total_minutes - sum(base)
        if remainder == 0:
            add(base)
        else:
            # try to fit remainder by adjusting last chunk
            if remainder >= policy.min_chunk and remainder <= policy.max_chunk and len(base) < policy.max_chunks:
                add(base + [remainder])
            else:
                # distribute remainder into last chunk if possible
                if base:
                    candidate = base[:-1] + [base[-1] + remainder]
                    add(candidate)

    # 3) two-chunk split around preferred
    if policy.max_chunks >= 2:
        half = total_minutes // 2
        add([half, total_minutes - half])

    # 4) min-chunk granular plan
    if policy.max_chunks >= 3:
        n = min(policy.max_chunks, max(2, total_minutes // policy.min_chunk))
        base = [total_minutes // n] * n
        # distribute remainder
        rem = total_minutes - sum(base)
        for i in range(rem):
            base[i % n] += 1
        # round to minutes (keep as-is)
        add(base)

    return plans[:max_plans]
