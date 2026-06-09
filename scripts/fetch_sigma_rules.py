#!/usr/bin/env python3
"""Wrapper – download Sigma rules into data/sigma_rules."""

import subprocess
import sys
from pathlib import Path

backend_script = Path(__file__).resolve().parent.parent / "backend" / "scripts" / "fetch_sigma_rules.py"
target = Path(__file__).resolve().parent.parent / "data" / "sigma_rules"
subprocess.run([sys.executable, str(backend_script), str(target)], check=True)
