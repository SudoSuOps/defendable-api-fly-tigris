from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.routes import healthz, ledger, pairs, records


def create_app() -> FastAPI:
    s = settings()
    app = FastAPI(
        title="DefendableAPI",
        description="The DefendableOS API · Fly.io + Tigris · Postgres swarm-and-bee · the cracked ledger ingestion + retrieval surface. Ring ring · to the shed.",
        version=__version__,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(healthz.router)
    app.include_router(records.router)
    app.include_router(ledger.router)
    app.include_router(pairs.router)

    @app.get("/")
    def root():
        return {
            "service": "defendable-api",
            "version": __version__,
            "doc": "https://defendabledocs.com/defendableledger/",
            "endpoints": ["/healthz", "/records", "/ledger/verify", "/ledger/stats", "/pairs"],
        }

    return app


app = create_app()
