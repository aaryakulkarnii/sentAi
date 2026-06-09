"""MITRE ATT&CK endpoints (Tier 2 matrix + coverage)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.alert import Alert
from app.models.mitre import MitreTechnique
from app.models.user import User

router = APIRouter()

# Canonical Enterprise ATT&CK tactic order (left → right in the matrix).
TACTIC_ORDER = [
    ("TA0043", "Reconnaissance"),
    ("TA0042", "Resource Development"),
    ("TA0001", "Initial Access"),
    ("TA0002", "Execution"),
    ("TA0003", "Persistence"),
    ("TA0004", "Privilege Escalation"),
    ("TA0005", "Defense Evasion"),
    ("TA0006", "Credential Access"),
    ("TA0007", "Discovery"),
    ("TA0008", "Lateral Movement"),
    ("TA0009", "Collection"),
    ("TA0011", "Command and Control"),
    ("TA0010", "Exfiltration"),
    ("TA0040", "Impact"),
]
TACTIC_RANK = {name: i for i, (_, name) in enumerate(TACTIC_ORDER)}


@router.get("/techniques")
async def list_techniques(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MitreTechnique))
    return result.scalars().all()


@router.get("/coverage")
async def coverage(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    """Alert counts per technique id (drives the heatmap)."""
    rows = await db.execute(
        select(Alert.mitre_technique_id, func.count(Alert.id))
        .where(Alert.mitre_technique_id.is_not(None))
        .group_by(Alert.mitre_technique_id)
    )
    return {tid: count for tid, count in rows.all()}


@router.get("/matrix")
async def matrix(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    """Tactics × techniques grid with per-technique detection coverage."""
    techniques = (await db.execute(select(MitreTechnique))).scalars().all()

    count_rows = (
        await db.execute(
            select(Alert.mitre_technique_id, func.count(Alert.id))
            .where(Alert.mitre_technique_id.is_not(None))
            .group_by(Alert.mitre_technique_id)
        )
    ).all()
    counts = {tid: count for tid, count in count_rows}

    grouped: dict[str, list] = {}
    for t in techniques:
        alert_count = counts.get(t.id, 0)
        grouped.setdefault(t.tactic, []).append(
            {
                "id": t.id,
                "technique": t.technique,
                "sub_technique": t.sub_technique,
                "covered": alert_count > 0,
                "alert_count": alert_count,
            }
        )

    tactics = [
        {
            "id": next((tid for tid, name in TACTIC_ORDER if name == tactic), None),
            "name": tactic,
            "techniques": sorted(techs, key=lambda x: x["id"]),
            "alert_count": sum(x["alert_count"] for x in techs),
        }
        for tactic, techs in grouped.items()
    ]
    tactics.sort(key=lambda t: TACTIC_RANK.get(t["name"], 99))

    return {
        "tactics": tactics,
        "total_techniques": len(techniques),
        "covered_techniques": sum(1 for t in techniques if counts.get(t.id, 0) > 0),
    }


@router.get("/techniques/{technique_id}")
async def get_technique(technique_id: str, db: AsyncSession = Depends(get_db)):
    t = await db.get(MitreTechnique, technique_id)
    if not t:
        raise HTTPException(404, "Technique not found")
    return t
