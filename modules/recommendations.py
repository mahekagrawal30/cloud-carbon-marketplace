"""Explainable, rule-based carbon reduction recommendations."""
from __future__ import annotations

import pandas as pd


def generate_recommendations(data: pd.DataFrame) -> pd.DataFrame:
    recommendations: list[dict[str, object]] = []
    for _, row in data.iterrows():
        emissions = float(row["emissions_kg_co2e"])
        service = str(row["service"])
        region = str(row["region"])
        if float(row["carbon_intensity_kg_per_kwh"]) > 0.45 and row["cleaner_alternative_region"] != region:
            savings = emissions * 0.70
            recommendations.append({
                "title": f"Assess migration from {region} to {row['cleaner_alternative_region']}",
                "category": "Cleaner region", "service": service, "region": region,
                "estimated_savings_kg": round(savings, 2), "priority": "High",
                "effort": "Medium", "cost_effect": "Review network and migration costs",
                "reason": "The current region has a relatively high estimated grid carbon intensity.",
            })
        if float(row["usage_hours"]) >= 700 and any(word in service.lower() for word in ("ec2", "virtual", "compute", "rds")):
            recommendations.append({
                "title": f"Right-size always-on {service}", "category": "Right-sizing",
                "service": service, "region": region, "estimated_savings_kg": round(emissions * 0.20, 2),
                "priority": "High", "effort": "Low", "cost_effect": "Likely lowers cloud spend",
                "reason": "The resource is active for nearly the entire month and should be reviewed for sizing or schedules.",
            })
        if float(row["usage_hours"]) < 550 and "storage" in service.lower():
            recommendations.append({
                "title": f"Apply archival policy to {service}", "category": "Storage lifecycle",
                "service": service, "region": region, "estimated_savings_kg": round(emissions * 0.15, 2),
                "priority": "Medium", "effort": "Low", "cost_effect": "Likely lowers storage spend",
                "reason": "Lower-use storage may be suitable for lifecycle or archival policies.",
            })
    if not recommendations:
        return pd.DataFrame(columns=["title", "category", "service", "region", "estimated_savings_kg", "priority", "effort", "cost_effect", "reason"])
    result = pd.DataFrame(recommendations).drop_duplicates(subset=["title", "service", "region"])
    return result.sort_values("estimated_savings_kg", ascending=False).reset_index(drop=True)
