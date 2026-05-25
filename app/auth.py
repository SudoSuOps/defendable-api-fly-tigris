from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from app.config import settings


def require_bearer(authorization: Optional[str] = Header(default=None)) -> None:
    expected = settings().api_bearer_token
    if not expected:
        return  # auth not configured · open mode
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    if authorization.removeprefix("Bearer ").strip() != expected:
        raise HTTPException(status_code=401, detail="invalid bearer token")
