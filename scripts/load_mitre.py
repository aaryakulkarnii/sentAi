#!/usr/bin/env python3
"""Download MITRE ATT&CK STIX bundle and seed mitre_techniques table."""

import asyncio
import json
import urllib.request
from pathlib import Path

STIX_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
OUT_PATH  = Path("data/mitre/enterprise-attack.json")


def download_stix() -> dict:
    if OUT_PATH.exists():
        print(f"Using cached {OUT_PATH}")
        return json.loads(OUT_PATH.read_text())
    print("Downloading MITRE ATT&CK STIX bundle…")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(STIX_URL) as r:
        data = json.loads(r.read())
    OUT_PATH.write_text(json.dumps(data))
    return data


async def seed(stix: dict) -> None:
    import sys; sys.path.insert(0, "backend")
    from app.db.postgres import AsyncSessionLocal, init_db
    from app.models.mitre import MitreTechnique

    await init_db()
    async with AsyncSessionLocal() as db:
        count = 0
        for obj in stix.get("objects", []):
            if obj.get("type") != "attack-pattern":
                continue
            ext = obj.get("external_references", [{}])[0]
            technique_id = ext.get("external_id", "")
            if not technique_id.startswith("T"):
                continue
            tactic = obj.get("kill_chain_phases", [{}])[0].get("phase_name", "")
            existing = await db.get(MitreTechnique, technique_id)
            if not existing:
                db.add(MitreTechnique(
                    id=technique_id,
                    tactic=tactic,
                    technique=obj.get("name", ""),
                    description=obj.get("description", "")[:2000] if obj.get("description") else None,
                    url=ext.get("url"),
                ))
                count += 1
        await db.commit()
        print(f"Seeded {count} MITRE techniques.")


if __name__ == "__main__":
    stix = download_stix()
    asyncio.run(seed(stix))
