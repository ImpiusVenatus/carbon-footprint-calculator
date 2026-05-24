from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import EmissionsSummaryResponse
from app.services.aggregator import get_emissions_summary

router = APIRouter(prefix="/emissions", tags=["emissions"])


@router.get("/summary", response_model=EmissionsSummaryResponse)
def emissions_summary(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    year: int = Query(default=2026),
):
    return get_emissions_summary(db, user.organization_id, year)
