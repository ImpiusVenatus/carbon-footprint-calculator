from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import AuditLog, User, UserRole
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/audit-log", tags=["audit-log"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_log(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.admin))],
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = (
        db.query(AuditLog, User.email)
        .join(User, AuditLog.user_id == User.id)
        .filter(AuditLog.organization_id == user.organization_id)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=email,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            metadata=log.metadata_,
            created_at=log.created_at,
        )
        for log, email in rows
    ]
