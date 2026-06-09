#!/bin/bash
set -e
echo "Running database migrations…"
alembic upgrade head
if [ ! -d "data/sigma_rules" ] || [ -z "$(find data/sigma_rules -name '*.yml' 2>/dev/null | head -1)" ]; then
  echo "Fetching Sigma rules…"
  python scripts/fetch_sigma_rules.py data/sigma_rules || echo "Sigma fetch skipped"
fi
echo "Starting application…"
exec "$@"
