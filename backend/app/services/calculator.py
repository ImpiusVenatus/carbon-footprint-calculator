from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Protocol


class FactorLike(Protocol):
    scope: str
    activity_unit: str
    factor_value: float | Decimal
    is_active: bool
    effective_year: int
    region: str


@dataclass(frozen=True)
class EmissionResult:
    co2e_kg: float
    scope: str
    factor_value_used: float
    calculated_at: datetime


def calculate_emission(
    quantity: float | Decimal,
    factor: FactorLike,
    *,
    unit: str,
    activity_year: int | None = None,
    activity_region: str | None = None,
) -> EmissionResult:
    qty = float(quantity)
    if qty <= 0:
        raise ValueError("Quantity must be greater than zero")

    if unit != factor.activity_unit:
        raise ValueError(
            f"Unit mismatch: entry unit '{unit}' does not match factor unit '{factor.activity_unit}'"
        )

    if not factor.is_active:
        raise ValueError("Emission factor is not active")

    if activity_year is not None and factor.effective_year != activity_year:
        raise ValueError(
            f"Factor effective year {factor.effective_year} does not match activity year {activity_year}"
        )

    if activity_region is not None and factor.region != activity_region:
        raise ValueError(
            f"Factor region '{factor.region}' does not match activity region '{activity_region}'"
        )

    factor_value = float(factor.factor_value)
    co2e_kg = qty * factor_value

    scope_value = factor.scope.value if hasattr(factor.scope, "value") else str(factor.scope)

    return EmissionResult(
        co2e_kg=co2e_kg,
        scope=scope_value,
        factor_value_used=factor_value,
        calculated_at=datetime.now(timezone.utc),
    )


def validate_period(period_start, period_end) -> None:
    if period_end < period_start:
        raise ValueError("period_end must not precede period_start")


def aggregate_emissions(emissions: list[float]) -> float:
    return sum(emissions)
