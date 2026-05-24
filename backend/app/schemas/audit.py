from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_email: str | None = None
    action: str
    entity_type: str
    entity_id: UUID | None
    metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
