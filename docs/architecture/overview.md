# SentinelAI – Architecture overview

## Layers

| Layer | Technologies | Responsibility |
|---|---|---|
| Ingestion | Beats, Kafka | Collect and stream telemetry |
| Processing | FastAPI workers | Normalise, detect, correlate, score |
| Intelligence | LangGraph, Qdrant | AI agent investigation pipeline |
| Storage | Postgres, OpenSearch, Redis, Qdrant | Persist all entities and logs |
| Presentation | Next.js | SOC operator interface |

## Event flow

```
Source logs
  → Beats collector
    → Kafka topic (sentinelai.{source})
      → Kafka consumer (FastAPI background task)
        → Normalizer (NormalizedEvent)
          → Sigma / Behavioral engine
            → Alert (Postgres + OpenSearch)
              → Correlation engine
                → Incident (Postgres)
                  → Risk scoring
                    → LangGraph agents
                      → Investigation (Postgres JSONB)
                        → Report (S3)
```

## Key design decisions

**Kafka as the spine** — all telemetry flows through Kafka regardless of source, giving
replay capability, backpressure control, and decoupled consumers.

**OpenSearch for logs, Postgres for entities** — raw logs belong in a search engine optimised
for full-text and time-series queries. Structured entities (users, incidents, assets) belong
in a relational store with ACID guarantees.

**LangGraph for agents** — the investigation pipeline is a stateful directed graph. Each node
is a specialised agent. The graph is compiled once and ainvoked per incident, with the full
state persisted to JSONB for auditability.

**Qdrant for RAG** — threat knowledge (ATT&CK, CVEs, playbooks) is embedded and stored as
vectors for semantic retrieval during investigation. This avoids stuffing entire knowledge
bases into every LLM context window.
