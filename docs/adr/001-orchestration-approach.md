# ADR 001: Orchestration approach

- Status: Accepted
- Date: 2026-03-02

## Context
MVP needs a reliable multi-agent flow with parallel provider calls and deterministic output without mandatory LLM keys.

## Decision
Use a small deterministic in-process state machine (`ShoppingRunOrchestrator`) rather than LangGraph for v1.

## Consequences
- Pros:
  - Fast to implement and debug.
  - Deterministic rankings in fallback mode.
  - No extra orchestration runtime dependency.
- Cons:
  - Less flexible graph composition than LangGraph.
  - Future dynamic tool routing requires refactoring.
