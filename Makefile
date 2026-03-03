.PHONY: infra-up infra-down api-dev web-dev

infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down

api-dev:
	cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web-dev:
	cd apps/web && pnpm dev --host --port 5173
