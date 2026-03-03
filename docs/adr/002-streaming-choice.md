# ADR 002: Streaming protocol choice

- Status: Accepted
- Date: 2026-03-02

## Context
UI requires near real-time progress updates for each agent stage and reconnect/replay support.

## Decision
Use WebSocket endpoint (`/runs/{run_id}/events`) with DB-persisted event history replay on connect.

## Consequences
- Pros:
  - Bidirectional channel allows future control messages.
  - Efficient low-latency event delivery.
  - Replay capability by reading `run_events` table.
- Cons:
  - Slightly more complex connection lifecycle than SSE.
