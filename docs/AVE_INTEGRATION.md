# AVE Cloud Skills Integration

AVERT uses the following AVE Cloud Data API endpoints to power its narrative rotation engine.

| AVE Endpoint | AVERT Feature | Purpose |
|---|---|---|
| `GET /ranks/topics` | Narrative Radar | Discover active on-chain narratives |
| `GET /ranks?topic={id}` | Candidate Board | Rank tokens within each narrative by investability |
| `GET /contracts/{token_id}` | Risk Assessment | Compute toxicity, route stability, and risk coverage per token |
| `GET /signals/public/list` | Signal Confirmation | Cross-reference candidate tokens against public trading signals |
| `GET /address/smart_wallet/list` | Smart Money Overlay | Detect smart wallet activity to enrich narrative strength |
| `GET /tokens/trending` | Trending Cross-Reference | Flag tokens that are independently trending on AVE |
| `GET /tokens/holders/{token_id}` | Holder Concentration | Assess top-holder risk for lead candidates |
| `GET /tokens/{token_id}` | Token Enrichment | Retrieve detailed metadata for top candidates |
| `GET /supported_chains` | Chain Awareness | Enumerate supported chains for multi-chain narrative tracking |
| `GET /klines/token/{token_id}` | Price Trend | 24h OHLCV trend for lead candidates |
| `POST /wallet/swap/quote` | Execution Preview | Real swap route, price impact, and gas estimate from AVE Trade API |
| `WSS price subscription` | Live Price Feed | Real-time price updates for active candidates via WebSocket |

## Integration Depth

AVERT does not simply mirror AVE data. It computes its own:
- **Narrative strength** from token-level flow, acceleration, breadth, persistence, and price expansion
- **Investability scores** combining leadership, liquidity, route stability, risk coverage, and smart flow alignment
- **Toxicity penalties** from contract risk flags including honeypot detection, mint methods, and tax analysis
- **Deterioration risk** from crowding, leader concentration, and risk drag
- **Stage bias** (WATCH/SCOUT/CONFIRM/ADD/TRIM/EXIT) derived deterministically from narrative and token metrics

## Track Coverage

AVERT qualifies for the **Complete Application** track by integrating both skill categories:

### Monitoring Skills
- Narrative detection from ranked topics
- Token risk assessment from contract analysis
- Smart wallet activity monitoring
- Trending token cross-reference
- Real-time price monitoring via WebSocket

### Trading Skills
- Swap quote preview via chain wallet Trade API
- Staged execution lifecycle (WATCH through COOLDOWN)
- Deterministic policy engine with protected exits
- Route quality and slippage assessment

AVE provides the substrate. AVERT provides the operating logic.
