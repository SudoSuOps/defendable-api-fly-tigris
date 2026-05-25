from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.config import settings
from app.db import db_health
from app.schemas import HealthOut
from app.storage import storage_health

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthOut)
async def healthz() -> HealthOut:
    s = settings()
    return HealthOut(
        ok=True,
        service="defendable-api",
        version=__version__,
        db=await db_health(),
        storage=storage_health(),
        auth_required=s.auth_required,
        bucket=s.tigris_bucket,
    )
