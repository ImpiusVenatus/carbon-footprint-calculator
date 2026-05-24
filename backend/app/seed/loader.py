from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import EmissionFactor, Scope
from app.seed.data import SEED_FACTORS


def seed_emission_factors(db: Session) -> int:
    existing = db.query(EmissionFactor).filter(EmissionFactor.organization_id.is_(None)).count()
    if existing > 0:
        return 0

    for item in SEED_FACTORS:
        factor = EmissionFactor(
            organization_id=None,
            scope=Scope(item["scope"]),
            category=item["category"],
            activity_unit=item["activity_unit"],
            factor_value=item["factor_value"],
            source=item["source"],
            effective_year=item["effective_year"],
            region=item["region"],
            is_active=True,
        )
        db.add(factor)

    db.commit()
    return len(SEED_FACTORS)


def main():
    db = SessionLocal()
    try:
        count = seed_emission_factors(db)
        print(f"Seeded {count} emission factors")
    finally:
        db.close()


if __name__ == "__main__":
    main()
