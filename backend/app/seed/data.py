"""DEFRA-style emission factor seed data (representative subset for portfolio demo)."""

SEED_FACTORS = [
    # Scope 1
    {"scope": "1", "category": "natural_gas", "activity_unit": "kWh", "factor_value": 0.183, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "1", "category": "diesel", "activity_unit": "litre", "factor_value": 2.687, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "1", "category": "petrol", "activity_unit": "litre", "factor_value": 2.169, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "1", "category": "refrigerant_r410a", "activity_unit": "kg", "factor_value": 2088.0, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    # Scope 2
    {"scope": "2", "category": "electricity", "activity_unit": "kWh", "factor_value": 0.207, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "2", "category": "electricity", "activity_unit": "kWh", "factor_value": 0.386, "source": "EPA eGRID 2024", "effective_year": 2024, "region": "US"},
    {"scope": "2", "category": "district_heating", "activity_unit": "kWh", "factor_value": 0.173, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    # Scope 3
    {"scope": "3", "category": "business_travel_air", "activity_unit": "km", "factor_value": 0.183, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "3", "category": "business_travel_rail", "activity_unit": "km", "factor_value": 0.035, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "3", "category": "employee_commuting", "activity_unit": "km", "factor_value": 0.171, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "3", "category": "waste_landfill", "activity_unit": "kg", "factor_value": 0.497, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "3", "category": "purchased_goods", "activity_unit": "kg", "factor_value": 3.2, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
    {"scope": "3", "category": "water_supply", "activity_unit": "m3", "factor_value": 0.149, "source": "DEFRA 2024", "effective_year": 2024, "region": "UK"},
]
