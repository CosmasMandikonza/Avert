# AVERT — Narrative Rotation Operating System

**Built on AVE Cloud Skills for the AVE Claw Hackathon 2026**

> Narratives first. Tokens second. Discipline everywhere.

AVERT watches on-chain narratives using AVE's ranked topic and token data, scores them by strength, velocity, and breadth, ranks the safest and most investable token expressions inside each theme, stages capital deployment through a lifecycle of WATCH → SCOUT → CONFIRM → ADD → TRIM → EXIT → COOLDOWN, and records every decision in a replayable discipline journal.

Instead of asking "should I buy this token?", AVERT asks: **where should capital rotate right now, how much belongs there, and when should that thesis be promoted, harvested, or killed?**

---

## Live Deployment

| Surface | URL |
|---------|-----|
| Frontend | [web-saferta.vercel.app](https://web-saferta.vercel.app) |
| Backend | [avert.onrender.com](https://avert.onrender.com) |
| API Snapshot | [avert.onrender.com/api/v1/snapshot](https://avert.onrender.com/api/v1/snapshot) |

---

## Quick Start (Local)

### Backend
```bash
cd apps/api
pip install -r requirements.txt
cp .env.example .env   # Set AVE_API_KEY and APP_MODE=LIVE_MODE
uvicorn app.main:app --port 8000
```

### Frontend
```bash
cd apps/web
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Product Surfaces

AVERT has seven operating surfaces, each serving a distinct role:

| Surface | Purpose |
|---------|---------|
| **Signal** | Live mode status, allocated capital, dry powder, open risk, persistent narrative context |
| **Radar** | Narratives compete for capital — strength, velocity, breadth, demand, deterioration |
| **Board** | Token candidates ranked by investability inside the active narrative |
| **Policy** | Deterministic gate stack controlling capital deployment with staged budgets |
| **Lifecycle** | Position state machine — WATCH through COOLDOWN with evidence |
| **Journal** | Decision accountability — rule trace, evidence stack, execution outcome |
| **Replay** | Step through narrative evolution and capital rotation history |

---

## AVE Cloud Skills Integration

AVERT integrates **13 AVE Cloud endpoints** across all three API surfaces:

### Data REST API
| Endpoint | AVERT Feature |
|----------|---------------|
| `GET /ranks/topics` | Narrative discovery |
| `GET /ranks?topic={id}` | Token ranking per narrative |
| `GET /contracts/{token_id}` | Risk assessment (toxicity, route stability) |
| `GET /signals/public/list` | Signal confirmation overlay |
| `GET /address/smart_wallet/list` | Smart money activity detection |
| `GET /tokens/trending` | Trending token cross-reference |
| `GET /tokens/holders/{id}` | Holder concentration analysis |
| `GET /tokens/{id}` | Token detail enrichment |
| `GET /supported_chains` | Multi-chain awareness |
| `GET /klines/token/{id}` | 24h price trend derivation |

### Trade REST API
| Endpoint | AVERT Feature |
|----------|---------------|
| `POST /wallet/swap/quote` | Execution preview with real route and output |

### WebSocket API
| Endpoint | AVERT Feature |
|----------|---------------|
| `WSS price subscription` | Real-time price monitoring |
| `WSS heartbeat` | Connection keep-alive |

### Integration Depth

AVERT does not simply display AVE data. It computes its own derived metrics:

- **Narrative strength** from token-level flow, acceleration, breadth, persistence, and price expansion
- **Investability scores** combining leadership, liquidity, route stability, risk coverage, and smart flow alignment
- **Toxicity penalties** from contract risk flags (honeypot, mint, blacklist, tax, proxy)
- **Deterioration risk** from crowding, leader concentration, and risk drag
- **Stage bias** derived deterministically from narrative and token metrics
- **Swap quote preview** using AVE's chain wallet Trade API

**AVE provides the on-chain substrate. AVERT provides the operating discipline.**

---

## Architecture

```
apps/
  api/                    # FastAPI backend
    app/
      main.py             # Routes, CORS, lifespan
      config.py           # Settings (env-driven)
      models.py           # DB models
      schemas.py          # Response schemas
      demo_seed.py        # Snapshot builder
      services/
        ave.py            # LiveAVEClient — 13 endpoint integration
        ave_contracts.py  # Typed Pydantic contracts for AVE payloads
        ave_trade.py      # Trade API swap quote client
        ave_wss.py        # WebSocket price monitor
        repository.py     # Snapshot repository with caching
        policy.py         # Deterministic policy engine
        state_machine.py  # 7-stage lifecycle
        execution.py      # Adapter-based execution (PAPER validated)
  web/                    # Next.js frontend
    app/                  # Route pages (signal, radar, candidates, etc.)
    components/avert/     # Operating surface components
    lib/                  # API client, types, computation
docs/
  AVE_INTEGRATION.md      # Full integration documentation
```

---

## Track Coverage

| Track | Features |
|-------|----------|
| **Monitoring Skills** | Narrative detection, token risk assessment, smart wallet monitoring, trending cross-reference, WSS price feed |
| **Trading Skills** | Swap quote preview via Trade API, staged execution lifecycle, deterministic policy with protected exits |
| **Complete Application** | End-to-end: discover → rank → allocate → execute → journal → replay |

---

## Judging Criteria

### Innovation (30%)
Narrative-first capital rotation is a novel operating model. The seven-stage lifecycle, deterministic policy engine, discipline journal, and thesis replay do not exist in any current on-chain tool.

### Technical Execution (30%)
Full-stack monorepo, 13 AVE endpoints, typed contracts, parallelized ingestion, adapter-based execution, snapshot caching with stale-on-error fallback, route-aware frontend shell.

### Real-World Value (40%)
AVERT solves undisciplined capital deployment — the most expensive problem in crypto trading. Staged lifecycles prevent FOMO. Deterministic gates prevent deployment without evidence. Toxicity scoring prevents exit liquidity traps. The journal creates institutional-grade accountability.

---

## License

Built for the AVE Claw Hackathon 2026.

---

**AVERT** — Narratives first. Tokens second. Discipline everywhere.