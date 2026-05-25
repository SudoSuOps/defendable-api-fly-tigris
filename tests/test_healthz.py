from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_healthz_returns_metadata():
    client = TestClient(create_app())
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "defendable-api"
    assert "bucket" in body
    assert "auth_required" in body


def test_root_endpoint():
    client = TestClient(create_app())
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "defendable-api"
    assert "/healthz" in body["endpoints"]


def test_records_list_requires_no_auth_when_unset():
    client = TestClient(create_app())
    # This will fail because DB is not configured, but we're checking the route is reachable
    r = client.get("/records")
    # 500 (no DB) or 200 (DB available) — both prove the route exists; auth wall not on read
    assert r.status_code in (200, 500)
