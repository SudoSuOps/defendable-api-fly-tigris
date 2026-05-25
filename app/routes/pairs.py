from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.db import session_scope
from app.models import Pair
from app.schemas import PairOut

router = APIRouter(prefix="/pairs", tags=["pairs"])


@router.get("", response_model=List[PairOut])
async def list_pairs(
    tier: Optional[str] = Query(default=None, regex="^(apex|honey|jelly|pollen|propolis)$"),
    limit: int = Query(default=50, ge=1, le=500),
    cursor_id: Optional[int] = Query(default=None),
) -> List[PairOut]:
    async with session_scope() as s:
        stmt = select(Pair).order_by(Pair.id.asc()).limit(limit)
        if tier:
            stmt = stmt.where(Pair.tier == tier)
        if cursor_id is not None:
            stmt = stmt.where(Pair.id > cursor_id)
        rows = (await s.execute(stmt)).scalars().all()
        return [PairOut.model_validate(p) for p in rows]


@router.get("/by-tier")
async def by_tier():
    async with session_scope() as s:
        rows = (
            await s.execute(select(Pair.tier, func.count(Pair.id)).group_by(Pair.tier))
        ).all()
        counts = {t: n for t, n in rows}
    return {
        "tiers": ["apex", "honey", "jelly", "pollen", "propolis"],
        "counts": {t: counts.get(t, 0) for t in ["apex", "honey", "jelly", "pollen", "propolis"]},
        "total": sum(counts.values()),
    }


@router.get("/{pair_id}", response_model=PairOut)
async def get_pair(pair_id: str) -> PairOut:
    async with session_scope() as s:
        row = (await s.execute(select(Pair).where(Pair.pair_id == pair_id))).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail=f"pair {pair_id} not found")
        return PairOut.model_validate(row)
