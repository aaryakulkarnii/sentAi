"""Portable column types that work on both PostgreSQL and SQLite.

In production we use Postgres JSONB; in DEV_MODE (SQLite) we fall back to the
generic JSON type. `with_variant` picks the right one per dialect automatically.
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB


def json_type():
    """Return a JSON column type: JSONB on Postgres, generic JSON elsewhere."""
    return JSON().with_variant(JSONB(), "postgresql")
