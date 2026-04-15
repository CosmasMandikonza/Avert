# AVERT Architecture

## System Architecture

AVERT is split into two product layers:

- `apps/web`: the operator-facing narrative rotation OS
- `apps/api`: the deterministic domain and data layer

The frontend consumes a single product snapshot shape that includes narratives, investable candidates, allocation policy, live positions, journal entries, and replay sessions. In local fallback mode, the frontend uses the same seeded snapshot structure as the backend. In container mode, it fetches `/api/v1/snapshot` from FastAPI.

## Repo Structure

```text
.
+-- apps
|   +-- api
|   |   +-- app
|   |   |   +-- domain
|   |   |   +-- services
|   |   |   +-- config.py
|   |   |   +-- database.py
|   |   |   +-- demo_seed.py
|   |   |   +-- main.py
|   |   |   +-- models.py
|   |   |   `-- schemas.py
|   |   +-- Dockerfile
|   |   `-- pyproject.toml
|   `-- web
|       +-- app
|       +-- components
|       |   +-- avert
|       |   `-- ui
|       +-- lib
|       +-- Dockerfile
|       `-- package.json
+-- docs
|   `-- architecture.md
+-- .env.example
+-- docker-compose.yml
`-- README.md
```

## Domain Model

### Primary entities

- `Narrative`: the top-level object for capital competition
- `NarrativeSignalSnapshot`: represented in the current repo by narrative evidence + score fields
- `CandidateToken`: token-level candidate inside a narrative
- `AllocationPlan`: narrative budget and deterministic gate bundle
- `Position`: staged capital state for an active or recently exited position
- `PolicyEvaluation`: explicit decision record for transition approval
- `ExecutionIntent`: execution preview or live execution request
- `JournalEntry`: replayable discipline ledger item
- `ReplaySession`: thesis playback session with ordered snapshots

### Narrative-first design

Narratives are first-class because token selection only makes sense inside a narrative context. AVERT treats the narrative as the capital bucket and tokens as ranked expression candidates within that bucket.

## Frontend Architecture

### Information architecture

- `/`: product landing and operating model
- `/radar`: narrative strength radar with evidence expansion
- `/candidates`: narrative-grouped investability board
- `/allocation`: capital contention and deterministic policy view
- `/positions`: staged position lifecycle surface
- `/journal`: expandable casefiles for discipline history
- `/replay`: thesis playback and replay timeline

### Design system

- Typography: `Syne`, `Manrope`, `IBM Plex Mono`
- Surface language: layered gradients, glass shards, atmospheric paneling
- Motion: dock-inspired route focus, slow hover float, expandable evidence cards
- Color system:
  - Ember `#F46A2C`
  - Coral `#FF8A5B`
  - Moss `#C7F36B`
  - Sea Glass `#8FE6D1`
  - Storm Ink `#112136`
  - Fog Blue `#D9E6F2`
  - Linen `#F6F1E8`
  - Plum `#342B3F`

### Data layer

`apps/web/lib/avert-api.ts` fetches a full snapshot from the backend when `AVERT_API_URL` is set. If it is not set, the same screens still run from the local seeded snapshot.

## Backend Architecture

### API surface

- `GET /api/v1/snapshot`: canonical frontend payload
- `POST /api/v1/policy/evaluate`: deterministic stage promotion check
- `POST /api/v1/execution/preview`: protected-exit-aware execution readiness preview
- `GET /api/v1/ave/topics`: AVE topic fetch adapter

### Service boundaries

- `domain/state_machine.py`: allowed capital stage transitions
- `domain/policy.py`: deterministic rule evaluation
- `services/ave.py`: demo and live AVE adapters
- `services/execution.py`: execution preview abstraction
- `services/repository.py`: persistence and seeded snapshot access

### Operating modes

- `DEMO_MODE`: seed-backed snapshot and replay environment
- `LIVE_MODE`: uses the live AVE adapter when `AVE_API_KEY` is present

## Database Schema

The current schema uses SQLAlchemy models backed by PostgreSQL JSON columns for structured evidence bundles and replay payloads.

### Tables

- `narratives`
  - ranking, velocity, breadth, evidence, token strip, stage bias
- `candidate_tokens`
  - investability score, toxicity, liquidity, overlap, protected exit
- `allocation_plans`
  - stage budgets, gate results, narrative-level exits
- `positions`
  - lifecycle stage, size, basis, PnL, stage progress, exits
- `policy_evaluations`
  - candidate, narrative, target stage, gates, allow/block result
- `execution_intents`
  - preview/live execution metadata and protected exit attachment
- `journal_entries`
  - replayable decision history with evidence bundle
- `replay_sessions`
  - ordered thesis playback snapshots

## State Machine

### Allowed transitions

- `WATCH -> SCOUT`
- `SCOUT -> CONFIRM | EXIT | COOLDOWN`
- `CONFIRM -> ADD | EXIT | COOLDOWN`
- `ADD -> TRIM | EXIT`
- `TRIM -> ADD | EXIT | COOLDOWN`
- `EXIT -> COOLDOWN`
- `COOLDOWN -> WATCH`

### Stage thresholds

- `SCOUT`: minimum narrative velocity and breadth
- `CONFIRM`: stronger breadth confirmation than scout
- `ADD`: highest narrative quality threshold
- `TRIM` and `EXIT`: no minimum threshold, because these are discipline-preserving actions

## Deterministic Policy Model

Current gate groups:

- valid state transition
- narrative strength
- risk sufficiency
- duplicate exposure
- execution readiness

A stage promotion is blocked if any gate resolves to `block`. A `watch` verdict does not block but communicates constrained sizing or operational caution.

## AVE Integration Layer

AVERT uses official AVE v2 endpoints as the live adapter surface:

- `GET /v2/ranks/topics`
- `GET /v2/ranks?topic={topic}`
- `GET /v2/contracts/{token-id}`

These endpoints align to the narrative-first operating model:

- topic ranks seed narrative competition
- ranked tokens by topic populate candidate sets
- contract risk data informs deterministic risk sufficiency

AVERT still computes its own internal narrative momentum velocity using flow, breadth, price expansion, and persistence rather than inheriting AVE topic rank as final truth.

## Demo / Replay Layer

Demo mode is an operating surface, not a fake UI mode.

- seeded narratives simulate live capital competition
- journal entries preserve approvals and blocks
- replay sessions step through thesis evolution over time
- execution preview simulates route readiness and protected exits

This makes the product usable for operator training, playbook review, and state-machine validation before live credentials are configured.

## Deployment Setup

### Containers

- `postgres`: PostgreSQL 16
- `api`: FastAPI service with SQLAlchemy schema bootstrapping
- `web`: standalone Next.js app

### Environment variables

- `APP_MODE`
- `DATABASE_URL`
- `AVE_API_BASE_URL`
- `AVE_API_KEY`
- `AVERT_API_URL`

### Local paths

- web: `http://localhost:3000`
- api: `http://localhost:8000`
- postgres: `localhost:5432`

## README Plan

The root README should continue to prioritize:

1. Product framing in one paragraph
2. Clear surface list
3. Local run instructions
4. Mode explanation
5. API surface summary
6. Direct link to architecture documentation
