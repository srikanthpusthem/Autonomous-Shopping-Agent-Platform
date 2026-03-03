# ADR 003: Data schema for MVP

- Status: Accepted
- Date: 2026-03-02

## Context
Need profile-aware recommendations, auditable run traces, and feedback memory persistence.

## Decision
Adopt normalized relational schema in Postgres with core entities:
`users`, `profiles`, `runs`, `run_events`, `product_snapshots`, `feedback`.

## Consequences
- Pros:
  - Clear ownership boundaries and query paths.
  - Persistent run trace for debugging/demo transparency.
  - Feedback can be folded back into planning deterministically.
- Cons:
  - JSONB payload fields trade strict schema for speed.
  - Additional migration work when payloads stabilize.
