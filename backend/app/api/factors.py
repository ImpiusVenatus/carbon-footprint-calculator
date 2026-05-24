from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles, write_audit_log
from app.database import get_db
from app.models import EmissionFactor, Scope, User, UserRole
from app.schemas import EmissionFactorCreate, EmissionFactorResponse, ScopeEnum

router = APIRouter(prefix="/factors", tags=["factors"])


def _scope_to_model(scope: ScopeEnum) -> Scope:
    return Scope(scope.value)


@router.get("", response_model=list[EmissionFactorResponse])
def list_factors(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    scope: ScopeEnum | None = None,
    category: str | None = None,
    year: int | None = None,
    region: str | None = None,
):
    query = db.query(EmissionFactor).filter(
        EmissionFactor.is_active.is_(True),
        (EmissionFactor.organization_id.is_(None)) | (EmissionFactor.organization_id == user.organization_id),
    )
    if scope:
        query = query.filter(EmissionFactor.scope == _scope_to_model(scope))
    if category:
        query = query.filter(EmissionFactor.category.ilike(f"%{category}%"))
    if year:
        query = query.filter(EmissionFactor.effective_year == year)
    if region:
        query = query.filter(EmissionFactor.region == region)
    return query.order_by(EmissionFactor.category).all()


@router.post("", response_model=EmissionFactorResponse, status_code=status.HTTP_201_CREATED)
def create_factor(
    payload: EmissionFactorCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin))],
):
    factor = EmissionFactor(
        organization_id=user.organization_id,
        scope=_scope_to_model(payload.scope),
        category=payload.category,
        activity_unit=payload.activity_unit,
        factor_value=payload.factor_value,
        source=payload.source,
        effective_year=payload.effective_year,
        region=payload.region,
    )
    db.add(factor)
    db.flush()
    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="created",
        entity_type="emission_factor",
        entity_id=factor.id,
    )
    db.commit()
    db.refresh(factor)
    return factor
