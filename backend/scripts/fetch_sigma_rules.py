#!/usr/bin/env python3
"""Download Sigma rules from the SigmaHQ repository."""

from __future__ import annotations

import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

SIGMA_ZIP_URL = "https://github.com/SigmaHQ/sigma/archive/refs/heads/master.zip"
CATEGORIES = [
    "sigma-master/rules/windows/process_creation",
    "sigma-master/rules/windows/builtin",
    "sigma-master/rules/linux/auditd",
    "sigma-master/rules/cloud/aws",
    "sigma-master/rules/network",
]


def fetch(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    if any(out_dir.rglob("*.yml")):
        print(f"Sigma rules already present in {out_dir}")
        return 0

    print("Downloading SigmaHQ rule set…")
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "sigma.zip"
        urllib.request.urlretrieve(SIGMA_ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)

        for category in CATEGORIES:
            src = Path(tmp) / category
            if not src.is_dir():
                print(f"  Skipping missing category: {category}")
                continue
            rel = Path(category).relative_to("sigma-master/rules")
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print(f"  Copied {category} → {dest}")

    total = len(list(out_dir.rglob("*.yml")))
    print(f"Installed {total} Sigma rules to {out_dir}")
    return total


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/sigma_rules")
    fetch(target)
