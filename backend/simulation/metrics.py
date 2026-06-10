"""GRIDSENTINEL-X Ω — Grid Health Metrics"""

import numpy as np


def calculate_metrics(grid_state: dict) -> dict:
    """Calculate comprehensive grid health metrics from state."""
    cities = grid_state.get("cities", [])
    all_lines = []
    all_trafos = []
    all_buses = []
    for c in cities:
        all_lines.extend(c.get("lines", []))
        all_trafos.extend(c.get("transformers", []))
        all_buses.extend(c.get("buses", []))

    # Voltage stability
    voltages = [b["voltage_pu"] for b in all_buses if "voltage_pu" in b]
    voltage_stability = 1.0 - np.std(voltages) * 10 if voltages else 0.5

    # Line loading risk
    loadings = [l["loading_percent"] for l in all_lines]
    avg_loading = np.mean(loadings) if loadings else 0
    max_loading = max(loadings) if loadings else 0
    overloaded = sum(1 for l in loadings if l > 80)

    # Transformer health
    trafo_healths = [t["health_score"] for t in all_trafos]
    avg_trafo_health = np.mean(trafo_healths) if trafo_healths else 1.0

    # Generation metrics
    total_gen = grid_state.get("total_generation_mw", 0)
    total_load = grid_state.get("total_load_mw", 0)
    reserve_margin = (total_gen - total_load) / total_gen if total_gen > 0 else 0

    # Renewable mix
    renewable_mw = 0
    total_cap = 0
    for c in cities:
        for g in c.get("generators", []):
            total_cap += g.get("capacity_mw", 0)
            if g.get("type") in ("Solar", "Wind", "Hydro"):
                renewable_mw += g.get("output_mw", 0)
    renewable_pct = (renewable_mw / total_gen * 100) if total_gen > 0 else 0

    # SAIDI estimate (simplified)
    critical_lines = sum(1 for l in all_lines if l.get("status") == "critical")
    estimated_saidi = critical_lines * 2.5  # hours

    return {
        "voltage_stability_index": round(float(np.clip(voltage_stability, 0, 1)), 3),
        "avg_line_loading_pct": round(float(avg_loading), 1),
        "max_line_loading_pct": round(float(max_loading), 1),
        "overloaded_lines": overloaded,
        "avg_transformer_health": round(float(avg_trafo_health), 3),
        "reserve_margin_pct": round(float(reserve_margin * 100), 1),
        "renewable_penetration_pct": round(float(renewable_pct), 1),
        "total_generation_mw": round(float(total_gen), 1),
        "total_load_mw": round(float(total_load), 1),
        "estimated_saidi_hours": round(float(estimated_saidi), 1),
        "n1_contingency_score": round(float(np.clip(1 - overloaded * 0.15, 0, 1)), 2),
        "national_health_score": grid_state.get("national_health_score", 0),
        "system_status": grid_state.get("status", "unknown"),
        "city_metrics": {
            c["city"]: {
                "health": c["health_score"],
                "generation_mw": c["total_generation_mw"],
                "load_mw": c["total_load_mw"],
                "status": c["status"],
            }
            for c in cities
        },
    }
