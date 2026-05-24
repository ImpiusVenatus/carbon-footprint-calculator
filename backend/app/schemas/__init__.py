from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class ScopeEnum(str, Enum):
    scope_1 = "1"
    scope_2 = "2"
    scope_3 = "3"


class UserRoleEnum(str, Enum):
    admin = "admin"
    contributor = "contributor"
    viewer = "viewer"


# Auth
class RegisterRequest(BaseModel):
    organization_name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: UserRoleEnum
    organization_id: UUID

    model_config = {"from_attributes": True}


# Emission factors
class EmissionFactorCreate(BaseModel):
    scope: ScopeEnum
    category: str = Field(min_length=1, max_length=255)
    activity_unit: str = Field(min_length=1, max_length=50)
    factor_value: float = Field(gt=0)
    source: str = Field(min_length=1, max_length=255)
    effective_year: int
    region: str = "UK"


class EmissionFactorResponse(BaseModel):
    id: UUID
    organization_id: UUID | None
    scope: ScopeEnum
    category: str
    activity_unit: str
    factor_value: float
    source: str
    effective_year: int
    region: str
    is_active: bool

    model_config = {"from_attributes": True}


# Activities
class ActivityCreate(BaseModel):
    emission_factor_id: UUID
    description: str = Field(min_length=1, max_length=500)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)
    period_start: datetime
    period_end: datetime

    @field_validator("period_end")
    @classmethod
    def validate_period(cls, period_end: datetime, info) -> datetime:
        period_start = info.data.get("period_start")
        if period_start and period_end.date() < period_start.date():
            raise ValueError("period_end must not precede period_start")
        return period_end


class ActivityUpdate(BaseModel):
    emission_factor_id: UUID | None = None
    description: str | None = Field(default=None, min_length=1, max_length=500)
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    period_start: datetime | None = None
    period_end: datetime | None = None


class EmissionResponse(BaseModel):
    id: UUID
    co2e_kg: float
    scope: ScopeEnum
    factor_value_used: float
    calculated_at: datetime

    model_config = {"from_attributes": True}


class ActivityResponse(BaseModel):
    id: UUID
    organization_id: UUID
    emission_factor_id: UUID
    description: str
    quantity: float
    unit: str
    period_start: datetime
    period_end: datetime
    created_by: UUID
    emission: EmissionResponse | None = None

    model_config = {"from_attributes": True}


class ActivityWithEmissionResponse(BaseModel):
    entry: ActivityResponse
    emission: EmissionResponse


# Import
class ImportPreviewRow(BaseModel):
    row_number: int
    category: str
    quantity: float
    unit: str
    period_start: str
    period_end: str
    valid: bool
    error: str | None = None
    emission_factor_id: UUID | None = None


class ImportPreviewResponse(BaseModel):
    rows: list[ImportPreviewRow]
    valid_count: int
    invalid_count: int


class ImportConfirmRequest(BaseModel):
    rows: list[dict[str, Any]]


# Emissions summary
class ScopeSummary(BaseModel):
    scope: str
    co2e_kg: float


class CategorySummary(BaseModel):
    category: str
    co2e_kg: float


class MonthlySummary(BaseModel):
    month: str
    co2e_kg: float


class TargetProgress(BaseModel):
    base_year_co2e: float
    current_co2e: float
    target_percent: float
    achieved_percent: float


class EmissionsSummaryResponse(BaseModel):
    total_co2e_kg: float
    by_scope: list[ScopeSummary]
    by_category: list[CategorySummary]
    monthly: list[MonthlySummary]
    target_progress: TargetProgress | None = None
    previous_year_co2e_kg: float | None = None
    yoy_change_percent: float | None = None


# Targets
class TargetCreate(BaseModel):
    scope: str = "all"
    base_year: int
    target_year: int
    reduction_percent: float = Field(gt=0, le=100)


class TargetResponse(BaseModel):
    id: UUID
    organization_id: UUID
    scope: str
    base_year: int
    target_year: int
    reduction_percent: float

    model_config = {"from_attributes": True}
