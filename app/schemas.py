from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

RecordType = Literal["GENESIS", "RECEIPT", "VERDICT", "PAIR", "DEED"]
Tier = Literal["apex", "honey", "jelly", "pollen", "propolis"]


class HealthOut(BaseModel):
    ok: bool
    service: str
    version: str
    db: bool
    storage: bool
    auth_required: bool
    bucket: str


class RecordIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ledger_seq: int
    record_id: str
    record_type: RecordType
    created_at: str
    parent_hash: str = Field(min_length=64, max_length=64)
    payload_ref: str
    payload_hash: str = Field(min_length=64, max_length=64)
    record_sha256: str = Field(min_length=64, max_length=64)
    issued_by: str
    host: str
    body: Dict[str, Any] = Field(default_factory=dict)


class RecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ledger_seq: int
    record_id: str
    record_type: str
    created_at: datetime
    parent_hash: str
    payload_ref: str
    payload_hash: str
    record_sha256: str
    issued_by: str
    host: str
    tigris_key: Optional[str] = None


class IngestResult(BaseModel):
    ok: bool
    record_id: str
    ledger_seq: int
    tigris_key: Optional[str]
    public_url: Optional[str]


class LedgerVerifyOut(BaseModel):
    ok: bool
    records_checked: int
    first_break_seq: Optional[int]
    errors: List[str]


class PairOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pair_id: str
    receipt_id: str
    verdict_id: str
    assignment_id: str
    tier: str
    pair_sha256: str
    tigris_key: Optional[str]
    created_at: datetime
