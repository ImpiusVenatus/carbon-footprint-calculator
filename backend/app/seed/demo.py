"""Seed a demo organization with sample activities for portfolio reviewers."""

from datetime import date

from sqlalchemy.orm import Session

from app.core.security import hash_password, write_audit_log
from app.database import SessionLocal
from app.models import (
    ActivityEntry,
    Emission,
    EmissionFactor,
    Organization,
    ReductionTarget,
    Scope,
    User,
    UserRole,
)
from app.seed.loader import seed_emission_factors
from app.services.calculator import calculate_emission

DEMO_EMAIL = "demo@carbonfootprint.app"
DEMO_PASSWORD = "Demo12345!"
DEMO_ORG = "Demo Corporation"

DEMO_ACTIVITIES = [
    ("electricity", 12000, "kWh", "2026-01-01", "2026-03-31", "HQ electricity Q1"),
    ("natural_gas", 5000, "kWh", "2026-01-01", "2026-03-31", "Office heating Q1"),
    ("diesel", 800, "litre", "2026-02-01", "2026-02-28", "Fleet fuel February"),
    ("business_travel_air", 4500, "km", "2026-01-15", "2026-01-20", "Client visit flights"),
    ("electricity", 10000, "kWh", "2025-01-01", "2025-12-31", "HQ electricity 2025"),
    ("natural_gas", 18000, "kWh", "2025-01-01", "2025-12-31", "Office heating 2025"),
]


def _find_factor(db: Session, category: str, unit: str) -> EmissionFactor | None:
    return (
        db.query(EmissionFactor)
        .filter(
            EmissionFactor.category == category,
            EmissionFactor.activity_unit == unit,
            EmissionFactor.organization_id.is_(None),
            EmissionFactor.is_active.is_(True),
        )
        .first()
    )


def seed_demo_data(db: Session) -> dict:
    seed_emission_factors(db)

    existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if existing:
        return {
            "created": False,
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD,
            "message": "Demo account already exists",
        }

    org = Organization(name=DEMO_ORG, industry="Technology", base_year=2025)
    db.add(org)
    db.flush()

    user = User(
        organization_id=org.id,
        email=DEMO_EMAIL,
        password_hash=hash_password(DEMO_PASSWORD),
        role=UserRole.admin,
    )
    db.add(user)
    db.flush()

    for category, qty, unit, start, end, desc in DEMO_ACTIVITIES:
        factor = _find_factor(db, category, unit)
        if not factor:
            continue
        entry = ActivityEntry(
            organization_id=org.id,
            emission_factor_id=factor.id,
            description=desc,
            quantity=qty,
            unit=unit,
            period_start=date.fromisoformat(start),
            period_end=date.fromisoformat(end),
            created_by=user.id,
        )
        db.add(entry)
        db.flush()
        result = calculate_emission(qty, factor, unit=unit)
        db.add(
            Emission(
                activity_entry_id=entry.id,
                organization_id=org.id,
                scope=Scope(result.scope),
                co2e_kg=result.co2e_kg,
                factor_value_used=result.factor_value_used,
                calculated_at=result.calculated_at,
            )
        )

    db.add(
        ReductionTarget(
            organization_id=org.id,
            scope="all",
            base_year=2025,
            target_year=2030,
            reduction_percent=30,
        )
    )

    write_audit_log(
        db,
        organization_id=org.id,
        user_id=user.id,
        action="created",
        entity_type="demo_seed",
        metadata={"activities": len(DEMO_ACTIVITIES)},
    )
    db.commit()

    return {
        "created": True,
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD,
        "organization": DEMO_ORG,
        "activities": len(DEMO_ACTIVITIES),
    }


def main():
    db = SessionLocal()
    try:
        result = seed_demo_data(db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
