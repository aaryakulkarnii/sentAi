#!/usr/bin/env python3
"""Download Sigma rules from the SigmaHQ repository.

Supports --force to re-download even if some rules already exist.
Only downloads categories that are missing or empty by default.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

SIGMA_ZIP_URL = "https://github.com/SigmaHQ/sigma/archive/refs/heads/master.zip"

# High-value rule categories that cover the biggest detection gaps:
# - Windows process_creation: Mimikatz, PowerShell abuse, LOLBins, persistence
# - Windows builtin: EventLog-based detections (logon, service install, etc.)
# - Windows powershell: Script block logging detections
# - Windows sysmon: Sysmon-specific detections
# - Linux auditd: Linux audit-based detections
# - Cloud AWS: CloudTrail-based detections
# - Network: DNS, firewall, proxy rule-based detections
CATEGORIES = [
    "sigma-master/rules/windows/process_creation",
    "sigma-master/rules/windows/builtin",
    "sigma-master/rules/windows/powershell",
    "sigma-master/rules/windows/sysmon",
    "sigma-master/rules/windows/registry",
    "sigma-master/rules/windows/file",
    "sigma-master/rules/linux/auditd",
    "sigma-master/rules/linux/process_creation",
    "sigma-master/rules/cloud/aws",
    "sigma-master/rules/cloud/azure",
    "sigma-master/rules/cloud/gcp",
    "sigma-master/rules/network",
]


def fetch(out_dir: Path, *, force: bool = False) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check which categories are already populated
    if not force:
        missing = []
        for category in CATEGORIES:
            rel = Path(category).relative_to("sigma-master/rules")
            dest = out_dir / rel
            if not dest.exists() or not any(dest.rglob("*.yml")):
                missing.append(category)
        if not missing:
            print(f"All Sigma rule categories already present in {out_dir}")
            return 0
        print(f"Missing {len(missing)} categories, downloading SigmaHQ rules...")
    else:
        missing = CATEGORIES
        print("Force mode: downloading all SigmaHQ rule categories...")

    print("Downloading SigmaHQ rule set...")
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "sigma.zip"
        urllib.request.urlretrieve(SIGMA_ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)

        for category in missing:
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
            count = len(list(dest.rglob("*.yml")))
            print(f"  Copied {category} -> {dest} ({count} rules)")

    total = len(list(out_dir.rglob("*.yml")))
    print(f"Installed {total} total Sigma rules in {out_dir}")
    return total


if __name__ == "__main__":
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]) if args else Path("data/sigma_rules")
    fetch(target, force=force)
