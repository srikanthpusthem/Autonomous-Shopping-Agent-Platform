# Architecture

## Components

```mermaid
flowchart LR
    UI[React Web App] -->|HTTP| API[FastAPI Backend]
    UI -->|WebSocket| WS[Run Events Stream]
    API --> DB[(Postgres)]
    API --> REDIS[(Redis)]
    API --> ORCH[Run Orchestrator]
    ORCH --> A1[PlannerAgent]
    ORCH --> A2[MarketplaceSearchAgents]
    ORCH --> A3[ReviewAnalyzerAgent]
    ORCH --> A4[DealCheckerAgent]
    ORCH --> A5[DecisionAgent]
    ORCH --> A6[MemoryAgent]
    A2 --> F1[(Amazon Fixture JSON)]
    A2 --> F2[(BestBuy Fixture JSON)]
```

## Agent flow

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web
    participant A as API
    participant O as Orchestrator
    participant P as Planner
    participant S as Search Agents
    participant R as Review Analyzer
    participant D as Deal Checker
    participant C as Decision
    participant M as Memory

    U->>W: Prompt + selected profile
    W->>A: POST /runs
    A->>O: start run
    O->>M: fetch preference feedback
    O->>P: create shopping plan
    O->>S: search adapters in parallel
    O->>R: summarize reviews
    O->>D: compute value score
    O->>C: rank top products
    O->>A: persist final output
    A-->>W: stream run events (WS)
    W-->>U: top 3 recs + tradeoffs
```

## Data model overview

- `users`: local auth identities (email/password hash).
- `profiles`: per-user shopping profiles and preferences.
- `runs`: lifecycle of each shopping run (`created -> planning -> searching -> analyzing -> ranking -> done|error`).
- `run_events`: persisted agent events for replay and live streaming.
- `product_snapshots`: candidate product artifacts captured during a run.
- `feedback`: user feedback signals (`pick`, `not_interested`, `preference`) used by MemoryAgent.

## Runtime behavior

- Run orchestration is deterministic and heuristics-based (no LLM dependency required).
- Provider adapters use local fixtures with simulated latency and timeout/error handling.
- Event streaming uses WebSocket with persisted history replay on reconnect.
