from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.services.calculator import EmissionResult, aggregate_emissions, calculate_emission, validate_period


@dataclass
class MockFactor:
    scope: str
    activity_unit: str
    factor_value: float | Decimal
    is_active: bool = True
    effective_year: int = 2024
    region: str = "UK"


class TestCalculateEmission:
    def test_correct_multiplication(self):
        factor = MockFactor(scope="2", activity_unit="kWh", factor_value=0.4)
        result = calculate_emission(1000, factor, unit="kWh")
        assert isinstance(result, EmissionResult)
        assert result.co2e_kg == 400.0
        assert result.scope == "2"
        assert result.factor_value_used == 0.4

    def test_unit_mismatch_raises(self):
        factor = MockFactor(scope="2", activity_unit="kWh", factor_value=0.4)
        with pytest.raises(ValueError, match="Unit mismatch"):
            calculate_emission(1000, factor, unit="litre")

    def test_zero_quantity_raises(self):
        factor = MockFactor(scope="2", activity_unit="kWh", factor_value=0.4)
        with pytest.raises(ValueError, match="greater than zero"):
            calculate_emission(0, factor, unit="kWh")

    def test_negative_quantity_raises(self):
        factor = MockFactor(scope="2", activity_unit="kWh", factor_value=0.4)
        with pytest.raises(ValueError, match="greater than zero"):
            calculate_emission(-100, factor, unit="kWh")

    def test_inactive_factor_raises(self):
        factor = MockFactor(scope="2", activity_unit="kWh", factor_value=0.4, is_active=False)
        with pytest.raises(ValueError, match="not active"):
            calculate_emission(100, factor, unit="kWh")

    def test_factor_snapshot_preserved(self):
        factor = MockFactor(scope="1", activity_unit="litre", factor_value=2.687)
        result = calculate_emission(50, factor, unit="litre")
        assert result.factor_value_used == 2.687
        assert result.co2e_kg == pytest.approx(134.35)
        assert result.calculated_at.tzinfo is not None


class TestValidatePeriod:
    def test_valid_period(self):
        validate_period(datetime(2026, 1, 1).date(), datetime(2026, 1, 31).date())

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError, match="period_end"):
            validate_period(datetime(2026, 2, 1).date(), datetime(2026, 1, 1).date())


class TestAggregateEmissions:
    def test_sums_to_known_total(self):
        emissions = [400.0, 134.35, 207.0]
        assert aggregate_emissions(emissions) == pytest.approx(741.35)

    def test_empty_list(self):
        assert aggregate_emissions([]) == 0
