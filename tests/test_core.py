from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.calculator import calculate_emissions
from modules.recommendations import generate_recommendations


def test_calculate_emissions():
    usage = pd.DataFrame([{"month": "2026-01", "provider": "AWS", "service": "EC2", "region": "test-region", "usage_hours": 720, "energy_kwh": 100, "cost_usd": 10}])
    factors = pd.DataFrame([{"region": "test-region", "carbon_intensity_kg_per_kwh": 0.5, "cleaner_alternative_region": "clean-region"}])
    result = calculate_emissions(usage, factors)
    assert result.loc[0, "emissions_kg_co2e"] == 50
    assert result.loc[0, "emissions_tonnes_co2e"] == 0.05


def test_recommendations_include_compute_right_sizing():
    usage = pd.DataFrame([{"month": "2026-01", "provider": "AWS", "service": "EC2", "region": "test-region", "usage_hours": 720, "energy_kwh": 100, "cost_usd": 10}])
    factors = pd.DataFrame([{"region": "test-region", "carbon_intensity_kg_per_kwh": 0.5, "cleaner_alternative_region": "clean-region"}])
    data = calculate_emissions(usage, factors)
    recommendations = generate_recommendations(data)
    assert "Right-sizing" in recommendations["category"].tolist()
