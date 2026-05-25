from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ledger_seq: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    record_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    record_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=_utc_now, nullable=False, index=True)
    parent_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    record_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_ref: Mapped[str] = mapped_column(Text, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    tigris_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_by: Mapped[str] = mapped_column(String(64), nullable=False)
    host: Mapped[str] = mapped_column(String(64), nullable=False)
    body: Mapped[dict] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index("ix_records_record_type_created_at", "record_type", "created_at"),
    )


class Pair(Base):
    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pair_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    receipt_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    verdict_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    assignment_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    tier: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    pair_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    tigris_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utc_now, nullable=False, index=True)
    record_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("records.id", ondelete="SET NULL"), nullable=True
    )
    body: Mapped[dict] = mapped_column(JSONB, nullable=False)

    record: Mapped["Record | None"] = relationship(lazy="joined")
