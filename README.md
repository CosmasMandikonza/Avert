# AVERT — Narrative Rotation Operating System

**Built on AVE Cloud Skills for the AVE Claw Hackathon 2026**

AVERT watches on-chain narratives using AVE's ranked topic and token data, scores them by strength, velocity, and breadth, ranks the safest and most investable token expressions inside each theme, stages capital deployment through a lifecycle of WATCH → SCOUT → CONFIRM → ADD → TRIM → EXIT → COOLDOWN, and records every decision in a replayable discipline journal.

Instead of asking "should I buy this token?", AVERT asks "where should capital rotate right now, how much belongs there, and when should that thesis be promoted, harvested, or killed?"

## Quick Start

### Backend
```bash
cd apps/api
cp .env.example .env  # Set AVE_API_KEY and APP_MODE=LIVE_MODE
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

### Frontend
```bash
cd apps/web
pnpm install
pnpm dev
```

Open http://localhost:3000 to see AVERT with live AVE data.

## AVE Cloud Skills Integration

See [docs/AVE_INTEGRATION.md](docs/AVE_INTEGRATION.md) for the full integration map.

## What Ships In This Repo

- `apps/web`: Next.js App Router frontend with all seven required product surfaces.
- `apps/api`: FastAPI backend with a narrative snapshot API, deterministic policy evaluation, execution previews, and an AVE adapter abstraction.
- `docker-compose.yml`: Postgres + API + web local stack.
- `docs/architecture.md`: System architecture, repo plan, state model, backend/frontend design, schema, and deployment notes.

## Product Surfaces

- Landing page
- Narrative Radar
- Candidate Board
- Allocation / Policy panel
- Position Lifecycle panel
- Discipline Journal
- Replay / Thesis Playback

## Core Product Behavior

1. Detect strengthening narratives from AVE topic and market data.
2. Rank the most investable tokens inside each narrative.
3. Deploy capital through `WATCH -> SCOUT -> CONFIRM -> ADD -> TRIM -> EXIT -> COOLDOWN`.
4. Enforce deterministic policy checks before promotion or execution.
5. Attach protected exits before trade approval.
6. Persist journal and replay data for every meaningful transition.

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui primitives with a custom AVERT design system
- Framer Motion
- FastAPI
- PostgreSQL
- Docker Compose

## Run Locally

### Full stack with Docker

```bash
docker compose up --build
```

The web container will call the API container through `AVERT_API_URL=http://api:8000`. The web app now expects backend snapshot truth in both `DEMO_MODE` and `LIVE_MODE`. If `AVERT_API_URL` is absent or the API is unavailable, the UI renders an explicit unavailable state instead of a local seeded fallback.

## API Endpoints

- `GET /health`
- `GET /api/v1/snapshot`
- `POST /api/v1/policy/evaluate`
- `POST /api/v1/execution/preview`
- `POST /api/v1/execution/submit`
- `GET /api/v1/execution/{request_id}`
- `GET /api/v1/ave/topics`

## Modes

- `DEMO_MODE`: canonical backend-owned demo snapshot, replay/test surface, deterministic policy and execution previews
- `LIVE_MODE`: live AVE ingestion path with explicit schema contracts, normalized live metrics, and adapter-backed execution availability checks

## Execution Validation

- `PAPER` is the validated end-to-end execution mode in this repo today. Preview, submit, status refresh, persistence, journal, and replay are all exercised through this path.
- `LIVE_CHAIN_WALLET` and `LIVE_PROXY_WALLET` are explicit adapter modes. They report `unavailable` unless `LIVE_MODE`, `LIVE_EXECUTION_ENABLED=true`, credentials, and a remote execution adapter endpoint are all configured.
- State-only transitions such as `WATCH`, `CONFIRM`, and `COOLDOWN` do not pretend to send live orders.

## Database Migrations

AVERT now uses Alembic instead of `Base.metadata.create_all`.

```bash
cd apps/api
.venv\Scripts\python -m pip install -e .
.venv\Scripts\alembic upgrade head
```

To create a new migration after schema changes:

```bash
cd apps/api
.venv\Scripts\alembic revision -m "describe change"
```

The app also runs `alembic upgrade head` automatically on startup when `AUTO_RUN_MIGRATIONS=true`.

## Live Validation

See [docs/live-validation.md](docs/live-validation.md) for the April 7, 2026 validation report covering:

- official AVE docs contracts confirmed against current examples
- unauthenticated live endpoint reachability checks
- the validated execution path in this repo
- remaining credential-gated limitations

## Next Product Work

- Add background ingestion jobs and caching around the live AVE snapshot path
- Wire real chain/proxy executor services behind the live execution adapter endpoints
- Wire authenticated operator workflows and audit trails

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full repo plan, domain model, state machine, schema, AVE integration notes, and deployment setup.
