from uuid import UUID

from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

from app.models import ActivityEntry, Emission, EmissionFactor, ReductionTarget, Scope
from app.schemas import (
    CategorySummary,
    EmissionsSummaryResponse,
    MonthlySummary,
    ScopeSummary,
    TargetProgress,
)


def _year_filter(year: int):
    return extract("year", ActivityEntry.period_start) == year


def get_emissions_summary(db: Session, organization_id: UUID, year: int) -> EmissionsSummaryResponse:
    base_query = (
        db.query(Emission)
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .join(EmissionFactor, ActivityEntry.emission_factor_id == EmissionFactor.id)
        .filter(
            Emission.organization_id == organization_id,
            _year_filter(year),
        )
    )

    total = (
        db.query(func.coalesce(func.sum(Emission.co2e_kg), 0))
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .filter(Emission.organization_id == organization_id, _year_filter(year))
        .scalar()
    )

    by_scope_rows = (
        db.query(Emission.scope, func.sum(Emission.co2e_kg))
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .filter(Emission.organization_id == organization_id, _year_filter(year))
        .group_by(Emission.scope)
        .all()
    )

    by_category_rows = (
        db.query(EmissionFactor.category, func.sum(Emission.co2e_kg))
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .join(EmissionFactor, ActivityEntry.emission_factor_id == EmissionFactor.id)
        .filter(Emission.organization_id == organization_id, _year_filter(year))
        .group_by(EmissionFactor.category)
        .order_by(func.sum(Emission.co2e_kg).desc())
        .all()
    )

    dialect = db.bind.dialect.name if db.bind else "sqlite"
    if dialect == "postgresql":
        month_expr = func.to_char(ActivityEntry.period_start, "YYYY-MM")
    else:
        month_expr = func.strftime("%Y-%m", ActivityEntry.period_start)

    monthly_rows = (
        db.query(month_expr.label("month"), func.sum(Emission.co2e_kg))
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .filter(Emission.organization_id == organization_id, _year_filter(year))
        .group_by(month_expr)
        .order_by(month_expr)
        .all()
    )

    scope_map = {"1": 0.0, "2": 0.0, "3": 0.0}
    for scope, total_kg in by_scope_rows:
        scope_map[scope.value if hasattr(scope, "value") else str(scope)] = float(total_kg or 0)

    by_scope = [ScopeSummary(scope=k, co2e_kg=v) for k, v in scope_map.items()]
    by_category = [
        CategorySummary(category=cat, co2e_kg=float(total_kg or 0)) for cat, total_kg in by_category_rows
    ]
    monthly = [MonthlySummary(month=m, co2e_kg=float(total_kg or 0)) for m, total_kg in monthly_rows]

    target_progress = _compute_target_progress(db, organization_id, year, float(total or 0))

    previous_total = (
        db.query(func.coalesce(func.sum(Emission.co2e_kg), 0))
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .filter(Emission.organization_id == organization_id, _year_filter(year - 1))
        .scalar()
    )
    prev = float(previous_total or 0)
    current = float(total or 0)
    yoy = round(((current - prev) / prev) * 100, 1) if prev > 0 else None

    return EmissionsSummaryResponse(
        total_co2e_kg=current,
        by_scope=by_scope,
        by_category=by_category,
        monthly=monthly,
        target_progress=target_progress,
        previous_year_co2e_kg=prev if prev > 0 else None,
        yoy_change_percent=yoy,
    )


def _compute_target_progress(
    db: Session, organization_id: UUID, current_year: int, current_co2e: float
) -> TargetProgress | None:
    target = (
        db.query(ReductionTarget)
        .filter(
            ReductionTarget.organization_id == organization_id,
            ReductionTarget.target_year >= current_year,
        )
        .order_by(ReductionTarget.target_year)
        .first()
    )
    if not target:
        return None

    base_total = (
        db.query(func.coalesce(func.sum(Emission.co2e_kg), 0))
        .join(ActivityEntry, Emission.activity_entry_id == ActivityEntry.id)
        .filter(
            Emission.organization_id == organization_id,
            extract("year", ActivityEntry.period_start) == target.base_year,
        )
        .scalar()
    )
    base_co2e = float(base_total or 0)
    if base_co2e <= 0:
        return TargetProgress(
            base_year_co2e=0,
            current_co2e=current_co2e,
            target_percent=float(target.reduction_percent),
            achieved_percent=0,
        )

    target_co2e = base_co2e * (1 - float(target.reduction_percent) / 100)
    reduction_needed = base_co2e - target_co2e
    reduction_achieved = base_co2e - current_co2e
    achieved_percent = max(0, min(100, (reduction_achieved / reduction_needed) * 100)) if reduction_needed > 0 else 0

    return TargetProgress(
        base_year_co2e=base_co2e,
        current_co2e=current_co2e,
        target_percent=float(target.reduction_percent),
        achieved_percent=round(achieved_percent, 1),
    )


def get_emissions_for_export(db: Session, organization_id: UUID, year: int) -> list[dict]:
    rows = (
        db.query(ActivityEntry, Emission, EmissionFactor)
        .join(Emission, Emission.activity_entry_id == ActivityEntry.id)
        .join(EmissionFactor, ActivityEntry.emission_factor_id == EmissionFactor.id)
        .filter(
            ActivityEntry.organization_id == organization_id,
            extract("year", ActivityEntry.period_start) == year,
        )
        .options(joinedload(ActivityEntry.emission_factor))
        .all()
    )

    return [
        {
            "description": entry.description,
            "category": factor.category,
            "scope": emission.scope.value if hasattr(emission.scope, "value") else str(emission.scope),
            "quantity": float(entry.quantity),
            "unit": entry.unit,
            "co2e_kg": float(emission.co2e_kg),
            "period_start": entry.period_start.isoformat(),
            "period_end": entry.period_end.isoformat(),
        }
        for entry, emission, factor in rows
    ]
