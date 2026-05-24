import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    contributor = "contributor"
    viewer = "viewer"


class Scope(str, enum.Enum):
    scope_1 = "1"
    scope_2 = "2"
    scope_3 = "3"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(255))
    reporting_year_start: Mapped[date | None] = mapped_column(Date)
    base_year: Mapped[int | None] = mapped_column(Integer)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    activity_entries: Mapped[list["ActivityEntry"]] = relationship(back_populates="organization")
    emissions: Mapped[list["Emission"]] = relationship(back_populates="organization")
    reduction_targets: Mapped[list["ReductionTarget"]] = relationship(back_populates="organization")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="organization")
    custom_factors: Mapped[list["EmissionFactor"]] = relationship(back_populates="organization")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.viewer)

    organization: Mapped["Organization"] = relationship(back_populates="users")
    activity_entries: Mapped[list["ActivityEntry"]] = relationship(back_populates="created_by_user")


class EmissionFactor(Base, TimestampMixin):
    __tablename__ = "emission_factors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    scope: Mapped[Scope] = mapped_column(Enum(Scope), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    factor_value: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_year: Mapped[int] = mapped_column(Integer, nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="UK")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    organization: Mapped["Organization | None"] = relationship(back_populates="custom_factors")
    activity_entries: Mapped[list["ActivityEntry"]] = relationship(back_populates="emission_factor")


class ActivityEntry(Base, TimestampMixin):
    __tablename__ = "activity_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    emission_factor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("emission_factors.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="activity_entries")
    emission_factor: Mapped["EmissionFactor"] = relationship(back_populates="activity_entries")
    created_by_user: Mapped["User"] = relationship(back_populates="activity_entries")
    emission: Mapped["Emission | None"] = relationship(
        back_populates="activity_entry", uselist=False, cascade="all, delete-orphan"
    )


class Emission(Base):
    __tablename__ = "emissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activity_entries.id"), nullable=False, unique=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    scope: Mapped[Scope] = mapped_column(Enum(Scope), nullable=False)
    co2e_kg: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    factor_value_used: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    activity_entry: Mapped["ActivityEntry"] = relationship(back_populates="emission")
    organization: Mapped["Organization"] = relationship(back_populates="emissions")


class ReductionTarget(Base, TimestampMixin):
    __tablename__ = "reduction_targets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    scope: Mapped[str] = mapped_column(String(10), nullable=False, default="all")
    base_year: Mapped[int] = mapped_column(Integer, nullable=False)
    target_year: Mapped[int] = mapped_column(Integer, nullable=False)
    reduction_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="reduction_targets")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="audit_logs")
