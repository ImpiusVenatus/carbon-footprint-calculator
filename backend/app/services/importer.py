import csv
import io
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import EmissionFactor


REQUIRED_COLUMNS = {"category", "quantity", "unit", "period_start", "period_end"}


def parse_csv_content(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("CSV file is empty or missing headers")
    headers = {h.strip().lower() for h in reader.fieldnames}
    if not REQUIRED_COLUMNS.issubset(headers):
        missing = REQUIRED_COLUMNS - headers
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    return [row for row in reader]


def preview_import(
    db: Session,
    organization_id: UUID,
    content: str,
    effective_year: int = 2024,
    region: str = "UK",
) -> list[dict]:
    rows = parse_csv_content(content)
    preview = []

    for idx, row in enumerate(rows, start=1):
        category = row.get("category", "").strip()
        unit = row.get("unit", "").strip()
        error = None
        factor_id = None
        quantity = 0.0
        valid = False

        try:
            quantity = float(row.get("quantity", "0"))
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero")
            period_start = row.get("period_start", "").strip()
            period_end = row.get("period_end", "").strip()
            datetime.strptime(period_start, "%Y-%m-%d")
            datetime.strptime(period_end, "%Y-%m-%d")
            if period_end < period_start:
                raise ValueError("period_end must not precede period_start")

            factor = (
                db.query(EmissionFactor)
                .filter(
                    EmissionFactor.category == category,
                    EmissionFactor.activity_unit == unit,
                    EmissionFactor.effective_year == effective_year,
                    EmissionFactor.region == region,
                    EmissionFactor.is_active.is_(True),
                    (EmissionFactor.organization_id.is_(None))
                    | (EmissionFactor.organization_id == organization_id),
                )
                .first()
            )
            if not factor:
                raise ValueError(f"No matching emission factor for category '{category}' and unit '{unit}'")
            factor_id = factor.id
            valid = True
        except ValueError as exc:
            error = str(exc)
            valid = False

        preview.append(
            {
                "row_number": idx,
                "category": category,
                "quantity": quantity,
                "unit": unit,
                "period_start": row.get("period_start", "").strip(),
                "period_end": row.get("period_end", "").strip(),
                "valid": valid,
                "error": error,
                "emission_factor_id": str(factor_id) if factor_id else None,
            }
        )

    return preview
