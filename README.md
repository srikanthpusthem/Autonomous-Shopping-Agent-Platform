# Autonomous Shopping Agent Platform

Monorepo for a multi-agent shopping copilot MVP.

## Structure
- `apps/api` FastAPI backend
- `apps/web` React + TypeScript + Vite frontend
- `packages/shared` shared contracts
- `infra` local infrastructure (Postgres + Redis)
- `docs` architecture and ADRs

## Quickstart (Step 1 scaffold)
1. Start infra:
   - `make infra-up`
2. Start API (after installing deps):
   - `make api-dev`
3. Start web (after installing deps):
   - `make web-dev`

## Env setup
- Copy `apps/api/.env.example` to `apps/api/.env`
- Copy `apps/web/.env.example` to `apps/web/.env`

