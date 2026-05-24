from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user, require_roles, write_audit_log
from app.database import get_db
from app.models import ActivityEntry, Emission, EmissionFactor, Scope, User, UserRole
from app.schemas import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    ActivityWithEmissionResponse,
    ImportConfirmRequest,
    ImportPreviewResponse,
    ImportPreviewRow,
)
from app.services.calculator import calculate_emission, validate_period
from app.services.importer import preview_import

router = APIRouter(prefix="/activities", tags=["activities"])


def _get_factor_for_org(db: Session, factor_id: UUID, organization_id: UUID) -> EmissionFactor:
    factor = (
        db.query(EmissionFactor)
        .filter(
            EmissionFactor.id == factor_id,
            EmissionFactor.is_active.is_(True),
            (EmissionFactor.organization_id.is_(None)) | (EmissionFactor.organization_id == organization_id),
        )
        .first()
    )
    if not factor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emission factor not found")
    return factor


def _persist_emission(db: Session, entry: ActivityEntry, factor: EmissionFactor) -> Emission:
    result = calculate_emission(entry.quantity, factor, unit=entry.unit)
    scope = Scope(result.scope)

    if entry.emission:
        entry.emission.co2e_kg = result.co2e_kg
        entry.emission.scope = scope
        entry.emission.factor_value_used = result.factor_value_used
        entry.emission.calculated_at = result.calculated_at
        emission = entry.emission
    else:
        emission = Emission(
            activity_entry_id=entry.id,
            organization_id=entry.organization_id,
            scope=scope,
            co2e_kg=result.co2e_kg,
            factor_value_used=result.factor_value_used,
            calculated_at=result.calculated_at,
        )
        db.add(emission)
    return emission


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    entries = (
        db.query(ActivityEntry)
        .options(joinedload(ActivityEntry.emission))
        .filter(ActivityEntry.organization_id == user.organization_id)
        .order_by(ActivityEntry.period_start.desc())
        .all()
    )
    return entries


@router.post("", response_model=ActivityWithEmissionResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.contributor))],
):
    factor = _get_factor_for_org(db, payload.emission_factor_id, user.organization_id)
    validate_period(payload.period_start.date(), payload.period_end.date())

    entry = ActivityEntry(
        organization_id=user.organization_id,
        emission_factor_id=factor.id,
        description=payload.description,
        quantity=payload.quantity,
        unit=payload.unit,
        period_start=payload.period_start.date(),
        period_end=payload.period_end.date(),
        created_by=user.id,
    )
    db.add(entry)
    db.flush()

    try:
        emission = _persist_emission(db, entry, factor)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="created",
        entity_type="activity_entry",
        entity_id=entry.id,
    )
    db.commit()
    db.refresh(entry)
    return ActivityWithEmissionResponse(entry=entry, emission=emission)


@router.put("/{activity_id}", response_model=ActivityWithEmissionResponse)
def update_activity(
    activity_id: UUID,
    payload: ActivityUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.contributor))],
):
    entry = (
        db.query(ActivityEntry)
        .options(joinedload(ActivityEntry.emission))
        .filter(ActivityEntry.id == activity_id, ActivityEntry.organization_id == user.organization_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    if payload.emission_factor_id:
        factor = _get_factor_for_org(db, payload.emission_factor_id, user.organization_id)
        entry.emission_factor_id = factor.id
    else:
        factor = _get_factor_for_org(db, entry.emission_factor_id, user.organization_id)

    if payload.description is not None:
        entry.description = payload.description
    if payload.quantity is not None:
        entry.quantity = payload.quantity
    if payload.unit is not None:
        entry.unit = payload.unit
    if payload.period_start is not None:
        entry.period_start = payload.period_start.date()
    if payload.period_end is not None:
        entry.period_end = payload.period_end.date()

    validate_period(entry.period_start, entry.period_end)

    try:
        emission = _persist_emission(db, entry, factor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="updated",
        entity_type="activity_entry",
        entity_id=entry.id,
    )
    db.commit()
    db.refresh(entry)
    return ActivityWithEmissionResponse(entry=entry, emission=emission)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.contributor))],
):
    entry = (
        db.query(ActivityEntry)
        .filter(ActivityEntry.id == activity_id, ActivityEntry.organization_id == user.organization_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="deleted",
        entity_type="activity_entry",
        entity_id=entry.id,
    )
    db.delete(entry)
    db.commit()


@router.post("/import/preview", response_model=ImportPreviewResponse)
async def import_preview(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.contributor))],
    file: UploadFile = File(...),
    year: int = 2024,
    region: str = "UK",
):
    content = (await file.read()).decode("utf-8-sig")
    try:
        rows = preview_import(db, user.organization_id, content, effective_year=year, region=region)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    preview_rows = [ImportPreviewRow(**row) for row in rows]
    valid_count = sum(1 for r in preview_rows if r.valid)
    return ImportPreviewResponse(
        rows=preview_rows,
        valid_count=valid_count,
        invalid_count=len(preview_rows) - valid_count,
    )


@router.post("/import/confirm", response_model=list[ActivityWithEmissionResponse])
def import_confirm(
    payload: ImportConfirmRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.contributor))],
):
    created: list[ActivityWithEmissionResponse] = []

    for row in payload.rows:
        factor_id = UUID(row["emission_factor_id"])
        factor = _get_factor_for_org(db, factor_id, user.organization_id)
        period_start = date.fromisoformat(row["period_start"])
        period_end = date.fromisoformat(row["period_end"])
        validate_period(period_start, period_end)

        entry = ActivityEntry(
            organization_id=user.organization_id,
            emission_factor_id=factor.id,
            description=f"{row['category']} import",
            quantity=float(row["quantity"]),
            unit=row["unit"],
            period_start=period_start,
            period_end=period_end,
            created_by=user.id,
        )
        db.add(entry)
        db.flush()
        emission = _persist_emission(db, entry, factor)
        created.append(ActivityWithEmissionResponse(entry=entry, emission=emission))

    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="imported",
        entity_type="activity_entry",
        metadata={"count": len(created)},
    )
    db.commit()
    for item in created:
        db.refresh(item.entry)
    return created
