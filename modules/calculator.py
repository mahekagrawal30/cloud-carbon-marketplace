"""Transparent, estimate-based cloud carbon calculations."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"month", "provider", "service", "region", "usage_hours", "energy_kwh", "cost_usd"}


def validate_usage_data(usage: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(usage.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if usage.empty:
        raise ValueError("The uploaded CSV does not contain any rows.")
    for column in ("usage_hours", "energy_kwh", "cost_usd"):
        values = pd.to_numeric(usage[column], errors="coerce")
        if values.isna().any() or (values < 0).any():
            raise ValueError(f"{column} must contain non-negative numeric values.")


def calculate_emissions(usage: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    """Match each usage record with a regional factor and calculate kg CO2e."""
    validate_usage_data(usage)
    factor_columns = {"region", "carbon_intensity_kg_per_kwh"}
    if not factor_columns.issubset(factors.columns):
        raise ValueError("Emission factors must contain region and carbon_intensity_kg_per_kwh.")

    data = usage.copy()
    for column in ("usage_hours", "energy_kwh", "cost_usd"):
        data[column] = pd.to_numeric(data[column])
    factor_data = factors[["region", "carbon_intensity_kg_per_kwh", "cleaner_alternative_region"]].copy()
    data = data.merge(factor_data, on="region", how="left")
    if data["carbon_intensity_kg_per_kwh"].isna().any():
        unknown = ", ".join(sorted(data.loc[data["carbon_intensity_kg_per_kwh"].isna(), "region"].unique()))
        raise ValueError(f"No emission factor is available for: {unknown}")
    data["emissions_kg_co2e"] = data["energy_kwh"] * data["carbon_intensity_kg_per_kwh"]
    data["emissions_tonnes_co2e"] = data["emissions_kg_co2e"] / 1000
    return data


def summary_metrics(data: pd.DataFrame) -> dict[str, float | str]:
    total_kg = float(data["emissions_kg_co2e"].sum())
    top_service = data.groupby("service")["emissions_kg_co2e"].sum().idxmax()
    top_region = data.groupby("region")["emissions_kg_co2e"].sum().idxmax()
    return {
        "total_kg": total_kg,
        "total_tonnes": total_kg / 1000,
        "total_cost": float(data["cost_usd"].sum()),
        "top_service": str(top_service),
        "top_region": str(top_region),
    }


def aggregate(data: pd.DataFrame, dimension: str) -> pd.DataFrame:
    return (
        data.groupby(dimension, as_index=False)
        .agg(emissions_kg_co2e=("emissions_kg_co2e", "sum"), cost_usd=("cost_usd", "sum"))
        .sort_values("emissions_kg_co2e", ascending=False)
    )
