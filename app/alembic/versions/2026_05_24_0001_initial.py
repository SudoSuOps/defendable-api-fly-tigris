"""initial · records + pairs tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-24 23:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("ledger_seq", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("record_id", sa.String(128), nullable=False, unique=True),
        sa.Column("record_type", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("parent_hash", sa.String(64), nullable=False),
        sa.Column("record_sha256", sa.String(64), nullable=False),
        sa.Column("payload_ref", sa.Text(), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("tigris_key", sa.Text(), nullable=True),
        sa.Column("issued_by", sa.String(64), nullable=False),
        sa.Column("host", sa.String(64), nullable=False),
        sa.Column("body", JSONB(), nullable=False),
    )
    op.create_index("ix_records_record_type", "records", ["record_type"])
    op.create_index("ix_records_created_at", "records", ["created_at"])
    op.create_index("ix_records_record_type_created_at", "records", ["record_type", "created_at"])

    op.create_table(
        "pairs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("pair_id", sa.String(128), nullable=False, unique=True),
        sa.Column("receipt_id", sa.String(128), nullable=False),
        sa.Column("verdict_id", sa.String(128), nullable=False),
        sa.Column("assignment_id", sa.String(128), nullable=False),
        sa.Column("tier", sa.String(16), nullable=False),
        sa.Column("pair_sha256", sa.String(64), nullable=False),
        sa.Column("tigris_key", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("record_id", sa.BigInteger(), sa.ForeignKey("records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("body", JSONB(), nullable=False),
    )
    op.create_index("ix_pairs_receipt_id", "pairs", ["receipt_id"])
    op.create_index("ix_pairs_verdict_id", "pairs", ["verdict_id"])
    op.create_index("ix_pairs_assignment_id", "pairs", ["assignment_id"])
    op.create_index("ix_pairs_tier", "pairs", ["tier"])
    op.create_index("ix_pairs_created_at", "pairs", ["created_at"])


def downgrade() -> None:
    op.drop_table("pairs")
    op.drop_table("records")
