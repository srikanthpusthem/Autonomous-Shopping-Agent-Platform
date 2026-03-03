# ADR 004: Background execution model

- Status: Accepted
- Date: 2026-03-02

## Context
MVP needs asynchronous run execution after `POST /runs` without operational overhead.

## Decision
Use FastAPI BackgroundTasks with `asyncio.run` wrapper per run instead of Celery in v1.

## Consequences
- Pros:
  - Minimal operational complexity.
  - No separate worker deployment required for MVP demos.
- Cons:
  - Not horizontally scalable like Celery workers.
  - Best for low-to-moderate concurrent demo traffic.
