# SentinelAI – System Architecture

## Overview

SentinelAI is a layered microservices architecture built around Kafka as the event spine, with FastAPI for processing and Next.js for the operator interface.

See also: [architecture/overview.md](architecture/overview.md) for a concise reference.

## Architecture Layers

| Layer | Technologies | Responsibility |
|---|---|---|
| Ingestion | Beats, Kafka | Collect and stream telemetry |
| Processing | FastAPI workers | Normalise, detect, correlate, score |
| Intelligence | LangGraph, Qdrant, OpenAI | AI agent investigation pipeline |
| Storage | Postgres, OpenSearch, Redis, Qdrant | Persist entities, logs, cache, vectors |
| Presentation | Next.js | SOC operator interface |

## Service Topology

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Frontend   │────▶│   Backend   │────▶│  PostgreSQL  │
│  (Next.js)  │     │  (FastAPI)  │     └──────────────┘
└─────────────┘     │             │────▶┌──────────────┐
                    │             │     │  OpenSearch  │
                    │             │────▶└──────────────┘
                    │             │────▶┌──────────────┐
                    │             │     │    Redis     │
                    │             │────▶└──────────────┘
                    │             │────▶┌──────────────┐
                    │             │     │    Qdrant    │
                    │             │────▶└──────────────┘
                    │             │
                    │             │◀───▶┌──────────────┐
                    └─────────────┘     │    Kafka     │
                          ▲           └──────────────┘
                          │                  ▲
                    ┌─────────────┐    ┌─────────────┐
                    │   Beats     │───▶│  Zookeeper  │
                    └─────────────┘    └─────────────┘
```

## Event Flow

```
Source logs
  → Beats collector
    → Kafka topic (sentinelai.{source})
      → Kafka consumer (FastAPI background task)
        → Normalizer (NormalizedEvent)
          → Enrichment (GeoIP, ASN, Asset)
            → OpenSearch index
            → Sigma / Behavioral engine
              → Alert (Postgres + OpenSearch)
                → Correlation engine
                  → Incident (Postgres)
                    → Risk scoring
                      → LangGraph agents
                        → Investigation (Postgres JSONB)
                          → Report (S3)
```

## Key Design Decisions

### Kafka as the spine

All telemetry flows through Kafka regardless of source. This provides replay capability, backpressure control, and decoupled consumers.

**Kafka listeners:**
- `kafka:29092` — internal Docker network (backend, beats)
- `localhost:9092` — host machine access (dev scripts)

### OpenSearch for logs, Postgres for entities

Raw logs belong in a search engine optimised for full-text and time-series queries. Structured entities (users, incidents, assets) belong in a relational store with ACID guarantees.

### LangGraph for agents

The investigation pipeline is a stateful directed graph. Each node is a specialised agent. The graph is compiled once and `ainvoke`d per incident, with full state persisted to JSONB for auditability.

### Qdrant for RAG

Threat knowledge (ATT&CK, CVEs, playbooks) is embedded and stored as vectors for semantic retrieval during investigation.

## API Structure

| Prefix | Purpose |
|---|---|
| `/api/v1/auth` | Login, current user |
| `/api/v1/alerts` | Alert CRUD |
| `/api/v1/incidents` | Incident management |
| `/api/v1/investigations` | Trigger and retrieve investigations |
| `/api/v1/mitre` | ATT&CK technique lookup |
| `/api/v1/threat-intel` | IOC and CVE search |
| `/api/v1/reports` | Report generation |
| `/health` | Dependency health probes |

## Data Models

| Table | Purpose |
|---|---|
| `users` | Authentication and RBAC |
| `assets` | Host inventory with criticality |
| `mitre_techniques` | ATT&CK technique catalogue |
| `detection_rules` | Sigma, behavioral, anomaly rules |
| `alerts` | Detection outputs |
| `incidents` | Correlated security events |
| `incident_alerts` | Alert-to-incident mapping |
| `incident_notes` | Analyst notes |
| `investigations` | AI agent output (JSONB) |
| `reports` | Generated report metadata |

## Schema Management

Database schema is managed by Alembic migrations (`backend/migrations/`). The backend entrypoint runs `alembic upgrade head` before starting.

## Infrastructure (Docker Compose)

| Service | Port | Description |
|---|---|---|
| frontend | 3000 | Next.js SOC dashboard |
| backend | 8000 | FastAPI REST + WebSocket |
| postgres | 5432 | Primary relational store |
| opensearch | 9200 | Log search |
| redis | 6379 | Cache and pub/sub |
| qdrant | 6333 | Vector store |
| kafka | 9092 (host) | Event bus |
| kafka-init | — | Topic bootstrap (one-shot) |
| opensearch-dashboards | 5601 | Log exploration |

## Security

- JWT authentication (HS256) with role-based access: `tier1`, `tier2`, `manager`, `engineer`
- Password hashing via bcrypt
- CORS restricted to configured origins
- OpenSearch security plugin disabled in development only

## Development Phases

| Tier | Focus |
|---|---|
| Tier 0 | Infrastructure, migrations, health checks, auth shell |
| Tier 1 | Data pipeline, detection, real-time alerts |
| Tier 2 | Correlation, incident management, MITRE matrix |
| Tier 3 | Threat intel, RAG, AI agents |
| Tier 4 | Reporting, cloud deployment, hardening |
