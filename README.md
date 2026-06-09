# SentinelAI

Autonomous AI-powered Security Operations Center platform.

## Quick start

```bash
cp .env.example .env
docker compose up -d
```

Frontend: http://localhost:3000  
API docs: http://localhost:8000/docs  
OpenSearch: http://localhost:9200  

## Services

| Service     | Port  | Description                          |
|-------------|-------|--------------------------------------|
| frontend    | 3000  | Next.js SOC dashboard                |
| backend     | 8000  | FastAPI REST + WebSocket             |
| postgres    | 5432  | Primary relational store             |
| opensearch  | 9200  | Log search and analytics             |
| redis       | 6379  | Session cache and pub/sub            |
| qdrant      | 6333  | Vector store for RAG                 |
| kafka       | 9092  | Event streaming bus                  |
| zookeeper   | 2181  | Kafka coordination                   |

## Development

```bash
# Backend only
cd backend && pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend only
cd frontend && npm install && npm run dev

# Seed admin user (after migrations)
python scripts/seed_db.py

# Fetch Sigma detection rules (first run)
python scripts/fetch_sigma_rules.py

# Seed MITRE ATT&CK data
python scripts/load_mitre.py

# Generate test events (host → localhost:9092)
python scripts/generate_test_events.py --count 1000
```

### Tier 1 pipeline

Events flow: **Kafka → normalize → enrich → OpenSearch → Sigma/behavioral detection → alert → WebSocket**.

Real-time alerts are pushed to the dashboard via `ws://localhost:8000/ws/alerts`.

Default admin credentials (after `seed_db.py`): `admin@sentinel.ai` / `changeme`

## Health check

`GET http://localhost:8000/health` probes Postgres, OpenSearch, Redis, Kafka, and Qdrant.

## Kafka

| Environment | Bootstrap server |
|---|---|
| Docker (backend, beats) | `kafka:29092` |
| Host machine | `localhost:9092` |

## Documentation

- [docs/PRD.md](docs/PRD.md) – product requirements
- [docs/architecture.md](docs/architecture.md) – system architecture
- [docs/architecture/overview.md](docs/architecture/overview.md) – concise reference
