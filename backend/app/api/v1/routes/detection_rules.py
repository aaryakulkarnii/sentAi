from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.user import User
from app.models.detection_rule import DetectionRule
from app.schemas.detection_rule import DetectionRuleResponse, DetectionRuleCreate, DetectionRuleUpdate

router = APIRouter()

def require_admin(user: User = Depends(get_current_user)):
    if user.role not in ["manager", "admin"]:
        raise HTTPException(403, "Insufficient permissions")
    return user

@router.get("/", response_model=list[DetectionRuleResponse])
async def list_rules(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),  # Anyone can view rules
):
    q = select(DetectionRule).order_by(DetectionRule.name.asc())
    return list((await db.execute(q)).scalars().all())


@router.post("/", response_model=DetectionRuleResponse)
async def create_rule(
    data: DetectionRuleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    rule = DetectionRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=DetectionRuleResponse)
async def toggle_rule(
    rule_id: str,
    data: DetectionRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    rule = await db.get(DetectionRule, rule_id)
    if not rule:
        raise HTTPException(404, "Rule not found")
        
    rule.enabled = data.enabled
    await db.commit()
    await db.refresh(rule)
    return rule

@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    rule = await db.get(DetectionRule, rule_id)
    if not rule:
        raise HTTPException(404, "Rule not found")
        
    await db.delete(rule)
    await db.commit()
    return {"status": "deleted"}
