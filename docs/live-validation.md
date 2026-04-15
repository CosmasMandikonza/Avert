# Live Validation Report

Date checked: April 7, 2026

## AVE Endpoints Confirmed

Official docs source:

- [AVE API v2 reference](https://docs.ave.ai/reference/api-reference/v2)

The current contract models in `apps/api/app/services/ave_contracts.py` were validated against the current official example payloads for:

- `GET /v2/ranks/topics`
- `GET /v2/ranks?topic={topic}`
- `GET /v2/contracts/{token-id}`

Validation command:

```bash
cd apps/api
.venv\Scripts\python scripts\validate_ave_contracts.py
```

Validation result on April 7, 2026:

- `/v2/ranks/topics`: passed against 20 documented topic records
- `/v2/ranks?topic={topic}`: passed against 2 documented ranked-token records
- `/v2/contracts/{token-id}`: passed against 1 documented risk-report payload

## Live Reachability Checks

Unauthenticated probes against the current live AVE base URL returned explicit auth failures, which confirms the endpoints are live but credential-gated:

- `GET https://prod.ave-api.com/v2/ranks/topics` -> `403` with `{"msg":"api key invalid"}`
- `GET https://prod.ave-api.com/v2/ranks?topic=ai` -> `403` with `{"msg":"api key invalid"}`
- `GET https://prod.ave-api.com/v2/contracts/{token-id}` -> `403` with `{"msg":"api key invalid"}`

Because no valid `AVE_API_KEY` was available in this environment, authenticated live payloads could not be re-fetched directly on April 7, 2026. AVERT therefore treats the docs-confirmed schema as authoritative and fails safely on malformed or incomplete live payloads.

## Important Contract Correction

`GET /v2/ranks/topics` currently exposes topic identity records, not topic momentum analytics. AVERT now derives narrative momentum from:

- ranked-token flow and volume from `GET /v2/ranks?topic={topic}`
- contract risk and route-quality signals from `GET /v2/contracts/{token-id}`

This removed the earlier assumption that topic-level flow and acceleration arrive directly from AVE.

## Execution Validation

Validated in-repo path:

- `PAPER`

Validated end-to-end behavior:

- preview lifecycle
- submit lifecycle
- persisted execution request and event history
- status refresh
- journal execution outcome rendering
- replay execution state rendering

Credential-gated but not validated in this environment:

- `LIVE_CHAIN_WALLET`
- `LIVE_PROXY_WALLET`

These modes are explicit about unavailable states and do not claim live readiness unless all of the following are true:

- `APP_MODE=LIVE_MODE`
- `LIVE_EXECUTION_ENABLED=true`
- wallet credentials are present
- remote execution adapter endpoints are configured

## Credibility Boundaries

- `DEMO_MODE` is backend-owned and canonical, but it is still a replay/test surface.
- `LIVE_MODE` is the real source-of-truth path for AVE-backed narrative computation.
- Live wallet execution remains adapter-dependent until a real executor service and credentials are configured.
