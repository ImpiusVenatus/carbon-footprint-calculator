import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, write_audit_log
from app.database import get_db
from app.models import User
from app.services.aggregator import get_emissions_for_export

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/export")
def export_report(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    year: int = Query(default=2026),
    format: str = Query(default="csv"),
):
    if format != "csv":
        return {"detail": "Only CSV export is supported in v1"}

    rows = get_emissions_for_export(db, user.organization_id, year)

    write_audit_log(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="exported",
        entity_type="report",
        metadata={"year": year, "format": format, "row_count": len(rows)},
    )
    db.commit()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("description,category,scope,quantity,unit,co2e_kg,period_start,period_end\n")

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="emissions_report_{year}.csv"'},
    )
