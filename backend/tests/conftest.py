"""Shared pytest configuration."""

import os
import contextlib
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("POSTGRES_PASSWORD", "test")

db_path = Path(__file__).resolve().parent.parent / "sentinel_dev.db"
with contextlib.suppress(FileNotFoundError):
    db_path.unlink()
