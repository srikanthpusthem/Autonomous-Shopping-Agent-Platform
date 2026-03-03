# Autonomous Shopping Agent Platform (MVP v1)

A demoable multi-agent shopping copilot built with FastAPI + React. It supports profile-aware planning, parallel marketplace search via mock adapters, review/deal analysis, deterministic ranking, and live run event streaming.

## Monorepo layout
- `apps/api` - FastAPI backend (Python 3.12+, SQLAlchemy 2.0, Alembic)
- `apps/web` - React + TypeScript + Vite + Tailwind frontend
- `packages/shared` - shared schemas/contracts placeholder
- `infra` - docker-compose for Postgres + Redis
- `docs` - architecture and ADRs

## Prerequisites
- Docker + Docker Compose
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- pnpm (preferred; via Corepack)

## Environment setup
1. API env:
   - `cp apps/api/.env.example apps/api/.env`
2. Web env:
   - `cp apps/web/.env.example apps/web/.env`

## Run commands
1. Start infrastructure:
   - `make infra-up`
2. Start API:
   - `make api-dev`
3. Start Web:
   - `make web-dev`

## API docs
- OpenAPI UI: `http://localhost:8000/docs`
- Health: `GET http://localhost:8000/health`

## MVP flow
1. Register/login.
2. Create/select a profile with budget, brand preferences, shipping preference, and use-case tags.
3. Start a shopping run from the copilot prompt.
4. Watch live agent events stream in the UI.
5. Review top 3 recommendations with reasoning/tradeoffs.
6. Submit feedback (`Pick this` / `Not interested`) to influence future runs.

## Validation commands
- API lint:
  - `make api-lint`
- API tests:
  - `make api-test`
- Web lint:
  - `make web-lint`

## Screenshots placeholders
- `docs/screenshots/login.png`
- `docs/screenshots/copilot-events.png`
- `docs/screenshots/recommendations.png`

## Troubleshooting
- `make api-lint` or `make api-test` fails with uv cache/sandbox errors:
  - rerun with normal local shell permissions (outside restricted sandbox environments).
- `make web-lint` fails because `pnpm` is not installed:
  - run `corepack enable` then `corepack prepare pnpm@latest --activate`.
- `corepack` cannot fetch pnpm due network restrictions:
  - install pnpm manually once network access is available, then run `make web-lint`.
- DB connection failures:
  - confirm `make infra-up` is running and `apps/api/.env` uses default localhost Postgres values.

## Notes
- Checkout/payment is intentionally out of scope for MVP.
- Provider integrations are fixture-backed (`MockAmazonAdapter`, `MockBestBuyAdapter`) for ToS-safe demoability.
