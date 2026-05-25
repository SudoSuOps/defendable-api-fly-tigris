from __future__ import annotations

import hashlib
from typing import List, Optional

import orjson
from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import session_scope
from app.models import Record
from app.schemas import LedgerVerifyOut

router = APIRouter(prefix="/ledger", tags=["ledger"])

ZERO_HASH = "0" * 64


def _recompute(row: Record) -> str:
    """Reproduce record_sha256 over the canonical record (record_sha256 stripped)."""
    body = {
        "ledger_seq": row.ledger_seq,
        "record_id": row.record_id,
        "record_type": row.record_type,
        "created_at": row.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parent_hash": row.parent_hash,
        "payload_ref": row.payload_ref,
        "payload_hash": row.payload_hash,
        "issued_by": row.issued_by,
        "host": row.host,
    }
    return hashlib.sha256(orjson.dumps(body, option=orjson.OPT_SORT_KEYS)).hexdigest()


@router.get("/verify", response_model=LedgerVerifyOut)
async def verify_chain() -> LedgerVerifyOut:
    async with session_scope() as s:
        rows = (await s.execute(select(Record).order_by(Record.ledger_seq.asc()))).scalars().all()

    errors: List[str] = []
    first_break: Optional[int] = None
    expected_parent = ZERO_HASH
    expected_seq = 0

    for row in rows:
        if row.ledger_seq != expected_seq:
            errors.append(f"seq gap at index: expected {expected_seq}, got {row.ledger_seq}")
            first_break = first_break if first_break is not None else row.ledger_seq
        if row.parent_hash != expected_parent:
            errors.append(f"chain break at seq {row.ledger_seq}: parent_hash mismatch")
            first_break = first_break if first_break is not None else row.ledger_seq
        expected_parent = row.record_sha256
        expected_seq = row.ledger_seq + 1

    return LedgerVerifyOut(
        ok=(not errors),
        records_checked=len(rows),
        first_break_seq=first_break,
        errors=errors[:20],
    )


@router.get("/stats")
async def stats():
    async with session_scope() as s:
        total = (await s.execute(select(func.count(Record.id)))).scalar_one()
        by_type = (
            await s.execute(
                select(Record.record_type, func.count(Record.id)).group_by(Record.record_type)
            )
        ).all()
        last_seq = (await s.execute(select(func.max(Record.ledger_seq)))).scalar_one()
    return {
        "total_records": total,
        "last_ledger_seq": last_seq,
        "by_type": {t: n for t, n in by_type},
    }
