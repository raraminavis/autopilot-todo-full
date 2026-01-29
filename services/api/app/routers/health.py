from __future__ import annotations
from fastapi import APIRouter
from ..schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(ok=True)
