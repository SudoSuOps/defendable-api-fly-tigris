from __future__ import annotations

import hashlib
from typing import List, Optional

import orjson
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.auth import require_bearer
from app.db import session_scope
from app.models import Record
from app.schemas import IngestResult, RecordIn, RecordOut
from app.storage import bucket as storage_bucket, get_object, put_object

router = APIRouter(prefix="/records", tags=["records"])

ZERO_HASH = "0" * 64


def _canonical(body) -> bytes:
    return orjson.dumps(body, option=orjson.OPT_SORT_KEYS)


def _recompute_record_sha256(rec: RecordIn) -> str:
    body = rec.model_dump(mode="json")
    body.pop("record_sha256", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


@router.post("", response_model=IngestResult, dependencies=[Depends(require_bearer)])
async def append_record(rec: RecordIn) -> IngestResult:
    """Append a single ledger record. Validates hash chain integrity against the latest stored record."""

    computed = _recompute_record_sha256(rec)
    if computed != rec.record_sha256:
        raise HTTPException(
            status_code=400,
            detail=f"record_sha256 mismatch: claimed={rec.record_sha256} computed={computed}",
        )

    async with session_scope() as s:
        last = (
            await s.execute(select(Record).order_by(Record.ledger_seq.desc()).limit(1))
        ).scalar_one_or_none()

        if last is None:
            if rec.ledger_seq != 0 or rec.parent_hash != ZERO_HASH:
                raise HTTPException(
                    status_code=400,
                    detail="first record must be genesis (ledger_seq=0, parent_hash=zeros)",
                )
        else:
            if rec.ledger_seq != last.ledger_seq + 1:
                raise HTTPException(
                    status_code=409,
                    detail=f"seq gap: expected {last.ledger_seq + 1}, got {rec.ledger_seq}",
                )
            if rec.parent_hash != last.record_sha256:
                raise HTTPException(
                    status_code=409,
                    detail=f"parent_hash mismatch: expected {last.record_sha256}",
                )

        key = f"records/{rec.record_type.lower()}/{rec.record_id}.json"
        put = put_object(key, _canonical(rec.body), content_type="application/json")

        row = Record(
            ledger_seq=rec.ledger_seq,
            record_id=rec.record_id,
            record_type=rec.record_type,
            parent_hash=rec.parent_hash,
            record_sha256=rec.record_sha256,
            payload_ref=rec.payload_ref,
            payload_hash=rec.payload_hash,
            tigris_key=put.key,
            issued_by=rec.issued_by,
            host=rec.host,
            body=rec.body,
        )
        s.add(row)
        await s.flush()

    return IngestResult(
        ok=True,
        record_id=rec.record_id,
        ledger_seq=rec.ledger_seq,
        tigris_key=put.key,
        public_url=put.public_url,
    )


@router.get("", response_model=List[RecordOut])
async def list_records(
    limit: int = Query(default=50, ge=1, le=500),
    cursor_seq: Optional[int] = Query(default=None, description="Return records with ledger_seq > cursor_seq"),
    record_type: Optional[str] = Query(default=None),
) -> List[RecordOut]:
    async with session_scope() as s:
        stmt = select(Record).order_by(Record.ledger_seq.asc()).limit(limit)
        if cursor_seq is not None:
            stmt = stmt.where(Record.ledger_seq > cursor_seq)
        if record_type:
            stmt = stmt.where(Record.record_type == record_type.upper())
        rows = (await s.execute(stmt)).scalars().all()
        return [RecordOut.model_validate(r) for r in rows]


@router.get("/{record_id}", response_model=RecordOut)
async def get_record(record_id: str) -> RecordOut:
    async with session_scope() as s:
        row = (
            await s.execute(select(Record).where(Record.record_id == record_id))
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail=f"record {record_id} not found")
        return RecordOut.model_validate(row)


@router.get("/{record_id}/body")
async def get_record_body(record_id: str):
    """Return the record body. Reads from Tigris if available, else from Postgres body column."""
    async with session_scope() as s:
        row = (
            await s.execute(select(Record).where(Record.record_id == record_id))
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail=f"record {record_id} not found")
        if row.tigris_key:
            blob = get_object(row.tigris_key)
            if blob is not None:
                return orjson.loads(blob)
        return row.body
