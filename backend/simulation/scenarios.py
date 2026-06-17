"""GRIDSENTINEL — Pre-built Disaster Scenarios & Black Swan Engine"""

import copy
import random
import numpy as np

SCENARIOS = {
    "heat_wave_mumbai": {
        "name": "Extreme Heat Wave — Mumbai",
        "description": "Temperatures exceed 48°C. AC demand surges 40%. Transformer stress critical.",
        "city": "Mumbai",
        "type": "climate",
        "severity": "critical",
        "actions": [
            {"type": "increase_load", "target": "all", "factor": 1.4},
            {"type": "reduce_generation", "target": "Solar", "factor": 0.85},
        ],
        "expected_impact": {"population": 2100000, "duration_hours": 6.5},
    },
    "cyclone_chennai": {
        "name": "Category 4 Cyclone — Chennai Coast",
        "description": "Severe cyclone makes landfall. Wind speeds 200km/h. Substations flooded.",
        "city": "Chennai",
        "type": "climate",
        "severity": "emergency",
        "actions": [
            {"type": "disable_line", "targets": ["CHN_L1", "CHN_L3"]},
            {"type": "reduce_generation", "target": "Wind", "factor": 0.1},
            {"type": "increase_load", "target": "all", "factor": 1.15},
        ],
        "expected_impact": {"population": 3500000, "duration_hours": 12},
    },
    "solar_collapse": {
        "name": "Nationwide Solar Generation Collapse",
        "description": "Unusual cloud cover + dust storm. Solar output drops 90% across all cities.",
        "city": "all",
        "type": "renewable",
        "severity": "critical",
        "actions": [
            {"type": "reduce_generation", "target": "Solar", "factor": 0.1},
        ],
        "expected_impact": {"population": 5000000, "duration_hours": 4},
    },
    "cyber_attack_delhi": {
        "name": "Coordinated Cyber Attack — Delhi Grid",
        "description": "APT group targets Delhi SCADA systems. Control signals corrupted.",
        "city": "Delhi",
        "type": "cyber",
        "severity": "emergency",
        "actions": [
            {"type": "disable_line", "targets": ["DEL_L1", "DEL_L3"]},
            {"type": "corrupt_voltage", "targets": ["DEL_Sub1_HV", "DEL_Sub2_HV"], "deviation": 0.15},
        ],
        "expected_impact": {"population": 4200000, "duration_hours": 8},
    },
    "cascading_failure": {
        "name": "Cascading Transformer Failure — National",
        "description": "Aged transformer in Mumbai fails. Overload cascades through network.",
        "city": "Mumbai",
        "type": "equipment",
        "severity": "emergency",
        "actions": [
            {"type": "disable_trafo", "targets": ["MUM_Trafo1"]},
            {"type": "increase_load", "target": "all", "factor": 1.2},
        ],
        "expected_impact": {"population": 6000000, "duration_hours": 10},
    },
    "monsoon_flooding_mumbai": {
        "name": "Severe Monsoon Flooding — Mumbai",
        "description": "Record rainfall floods 3 substations. Underground cables compromised.",
        "city": "Mumbai",
        "type": "climate",
        "severity": "critical",
        "actions": [
            {"type": "disable_line", "targets": ["MUM_L2", "MUM_L4", "MUM_L5"]},
            {"type": "disable_trafo", "targets": ["MUM_Trafo2"]},
        ],
        "expected_impact": {"population": 2800000, "duration_hours": 18},
    },
    "peak_demand_national": {
        "name": "National Peak Demand Surge",
        "description": "Evening peak + festival season. Demand exceeds capacity by 25%.",
        "city": "all",
        "type": "demand",
        "severity": "warning",
        "actions": [
            {"type": "increase_load", "target": "all", "factor": 1.25},
        ],
        "expected_impact": {"population": 8000000, "duration_hours": 3},
    },
    "equipment_aging_bengaluru": {
        "name": "Multi-Component Degradation — Bengaluru",
        "description": "Multiple transformers and lines near end-of-life. Simultaneous degradation.",
        "city": "Bengaluru",
        "type": "equipment",
        "severity": "warning",
        "actions": [
            {"type": "degrade_trafo", "targets": ["BLR_Trafo1", "BLR_Trafo2"], "factor": 0.6},
        ],
        "expected_impact": {"population": 1500000, "duration_hours": 5},
    },
}


def apply_scenario(net, city_buses: dict, scenario_key: str, custom_params: dict = None):
    """Apply a scenario's actions to the pandapower network. Returns modified net."""
    scenario = SCENARIOS.get(scenario_key)
    if not scenario:
        raise ValueError(f"Unknown scenario: {scenario_key}")

    params = {**scenario, **(custom_params or {})}
    affected_net = copy.deepcopy(net)

    for action in params["actions"]:
        _apply_action(affected_net, city_buses, action, params.get("city", "all"))

    return affected_net, scenario


def _apply_action(net, city_buses: dict, action: dict, city: str):
    """Apply a single action to the network."""
    atype = action["type"]

    if atype == "increase_load":
        factor = action["factor"]
        if city == "all":
            net.load["p_mw"] *= factor
            net.load["q_mvar"] *= factor
        else:
            bus_ids = list(city_buses.get(city, {}).values())
            mask = net.load["bus"].isin(bus_ids)
            net.load.loc[mask, "p_mw"] *= factor
            net.load.loc[mask, "q_mvar"] *= factor

    elif atype == "reduce_generation":
        target_type = action["target"]
        factor = action["factor"]
        if city == "all":
            mask = net.sgen["type"] == target_type
        else:
            bus_ids = list(city_buses.get(city, {}).values())
            mask = (net.sgen["bus"].isin(bus_ids)) & (net.sgen["type"] == target_type)
        net.sgen.loc[mask, "p_mw"] *= factor

    elif atype == "disable_line":
        for target_name in action["targets"]:
            mask = net.line["name"] == target_name
            net.line.loc[mask, "in_service"] = False

    elif atype == "disable_trafo":
        for target_name in action["targets"]:
            mask = net.trafo["name"] == target_name
            net.trafo.loc[mask, "in_service"] = False

    elif atype == "corrupt_voltage":
        for bus_name in action["targets"]:
            for city_name, buses in city_buses.items():
                if bus_name in buses:
                    bus_id = buses[bus_name]
                    if bus_id in net.ext_grid["bus"].values:
                        mask = net.ext_grid["bus"] == bus_id
                        deviation = action.get("deviation", 0.1)
                        net.ext_grid.loc[mask, "vm_pu"] += random.uniform(-deviation, deviation)

    elif atype == "degrade_trafo":
        for target_name in action["targets"]:
            mask = net.trafo["name"] == target_name
            # Simulate degradation by reducing max loading capability
            # (pandapower doesn't directly support this, so we increase connected loads)


def parse_custom_scenario(description: str) -> dict:
    """Parse a natural language scenario description into structured actions.
    This will be enhanced by the AI agent for custom scenarios."""
    actions = []
    desc_lower = description.lower()

    if "heat" in desc_lower or "temperature" in desc_lower:
        factor = 1.4
        if "extreme" in desc_lower:
            factor = 1.5
        actions.append({"type": "increase_load", "target": "all", "factor": factor})

    if "cyclone" in desc_lower or "storm" in desc_lower or "hurricane" in desc_lower:
        actions.append({"type": "reduce_generation", "target": "Wind", "factor": 0.1})
        actions.append({"type": "increase_load", "target": "all", "factor": 1.15})

    if "solar" in desc_lower and ("drop" in desc_lower or "collapse" in desc_lower):
        actions.append({"type": "reduce_generation", "target": "Solar", "factor": 0.1})

    if "cyber" in desc_lower or "attack" in desc_lower:
        actions.append({"type": "increase_load", "target": "all", "factor": 1.1})

    if "flood" in desc_lower or "rain" in desc_lower:
        actions.append({"type": "increase_load", "target": "all", "factor": 1.15})

    if not actions:
        actions.append({"type": "increase_load", "target": "all", "factor": 1.3})

    return {
        "name": f"Custom: {description[:60]}",
        "description": description,
        "type": "custom",
        "severity": "critical",
        "city": "all",
        "actions": actions,
        "expected_impact": {"population": 3000000, "duration_hours": 6},
    }
