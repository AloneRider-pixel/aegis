# Aegis Architecture

```mermaid
flowchart LR
    UI[React UI] --> API[FastAPI API]
    API --> AUTH[JWT Auth]
    API --> DB[(PostgreSQL + pgvector)]
    API --> REDIS[(Redis)]
    API --> AGENT[LangGraph Investigation Graph]
    AGENT --> TOOLS[Telemetry / Knowledge Tools]
    AGENT --> LLM[LLM Provider]
    AGENT --> DB
    API --> AUDIT[Audit Log]
    AGENT --> OBS[Investigation Trace]
    OBS --> UI
```

## Control flow

1. Authenticate the operator.
2. Create or inspect an incident.
3. Run the investigation graph to collect evidence and evaluate hypotheses.
4. Persist root-cause analysis, evidence, and investigation trace.
5. Gate remediation behind explicit approval.
6. Execute only an approved remediation, with dry-run as the default safety mode.

## Reliability boundaries

- PostgreSQL is the durable system of record.
- Redis supports transient state and rate-limiting concerns.
- AI outputs are treated as recommendations backed by evidence rather than autonomous authority.
- Auditability is maintained through incident events and investigation traces.
