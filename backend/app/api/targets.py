from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles, write_audit_log
from app.database import get_db
from app.models import ReductionTarget, User, UserRole
from app.schemas import TargetCreate, TargetResponse

router = APIRouter(prefix="/targets", tags=["targets"])


@router.get("", response_model=list[TargetResponse])
def list_targets(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return (
        db.query(ReductionTarget)
        .filter(ReductionTarget.organization_id == user.organization_id)
        .order_by(ReductionTarget.target_year)
        .all()
    )


@router.post("", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
def create_target(
    payload: TargetCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin))],
):
    target = ReductionTarget(
        organization_id=user.organization_id,
        scope=payload.scope,
        base_year=payload.base_year,
        target_year=payload.target_year,
        reduction_percent=payload.reduction_percent,
    )
    db.add(target)
    db.flush()
    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="created",
        entity_type="reduction_target",
        entity_id=target.id,
    )
    db.commit()
    db.refresh(target)
    return target
