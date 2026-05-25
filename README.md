# defendable-api-fly-tigris

**The DefendableOS API · Fly.io + Tigris object storage · Postgres `swarm-and-bee`.**

The ingestion + retrieval surface for the cracked ledger. The bridge between the sovereign GPU compute on smash (DefendableRouter spine · SwarmCurator-9B) and the public publication layer at [defendableledger.com](https://defendableledger.com). Ring ring · to the shed.

## What this is

A FastAPI app that:

- Accepts hash-chained DefendableLedger records (receipts · verdicts · pairs · deeds) and stores them in Postgres + Tigris
- Verifies hash-chain integrity over the entire ledger
- Serves records and SwarmJelly training pairs publicly
- Runs on Fly.io · Postgres `swarm-and-bee` attached · Tigris S3-compat bucket attached

## What this is NOT

- Not a write endpoint with loose schema · every append must satisfy `record_sha256` recomputation AND chain integrity
- Not a generic CRUD API · the ledger is append-only
- Not the GPU compute layer · SwarmCurator lives on smash
- Not the spine · the DefendableRouter spine lives on smash too

## Architecture

```
DefendableRouter spine (smash · sovereign GPU)
  │  hash-chained records written locally
  ▼
defendable-api (Fly.io · this repo)
  ├─ Postgres swarm-and-bee  (canonical record store + indexes)
  └─ Tigris bucket           (raw record bodies · S3-compat · public URL)
  ▼
defendableledger.com         (CF Pages · reads /records via API or fetches Tigris keys)
```

## Endpoints

| method | path | purpose |
|---|---|---|
| GET  | `/healthz`         | service + db + storage + bucket + auth-required reflection |
| GET  | `/`                | root info + endpoint index |
| POST | `/records`         | **append** a single hash-chained record (auth required if `API_BEARER_TOKEN` set · validates record_sha256 + parent_hash + ledger_seq) |
| GET  | `/records`         | list records (paginated · filter by `record_type`) |
| GET  | `/records/{id}`    | get record metadata |
| GET  | `/records/{id}/body` | fetch record body (Tigris if present · else Postgres) |
| GET  | `/ledger/verify`   | walk chain · verify every parent_hash + record_sha256 |
| GET  | `/ledger/stats`    | totals + by-type counts + last ledger_seq |
| GET  | `/pairs`           | list training pairs (filter by `tier`) |
| GET  | `/pairs/by-tier`   | Royal Jelly counts (apex · honey · jelly · pollen · propolis) |
| GET  | `/pairs/{id}`      | get pair metadata |

## Stack

- Python 3.12
- FastAPI · uvicorn · pydantic v2 · pydantic-settings
- SQLAlchemy 2 (async) + asyncpg
- Alembic (migrations)
- boto3 (Tigris S3-compat)
- orjson · httpx

## Local development

```bash
cp .env.example .env
# fill in DATABASE_URL + AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY

python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"

# DB migrations
alembic upgrade head

# Run
uvicorn app.main:app --reload --port 8080

# Tests
pytest -q
```

## Deploy to Fly.io

```bash
# First time:
fly launch --no-deploy           # accept defaults, app name: defendable-api
fly postgres attach swarm-and-bee  # attaches DATABASE_URL secret
fly storage create defendable-ledger  # creates Tigris bucket + AWS_* secrets

# Set the bearer token (rotate as needed):
fly secrets set API_BEARER_TOKEN=$(openssl rand -hex 32)

# Deploy:
fly deploy
```

The Dockerfile runs `alembic upgrade head` before starting uvicorn, so migrations apply automatically on deploy.

## Auth model

- All write endpoints (`POST /records`) require `Authorization: Bearer <token>` matching `API_BEARER_TOKEN`.
- All read endpoints are public (records are public proof — that's the whole point).
- If `API_BEARER_TOKEN` is unset, the auth check is bypassed (development mode only).

## Doctrine

Operator-grade. Books and records. Class A 5-cap. No fluff. Sovereign by default · external storage is the publication mirror, not the source of truth (the spine on smash owns the canonical state).

The cracked ledger compounds. To the shed.
