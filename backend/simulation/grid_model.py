"""GRIDSENTINEL — 4-City National Power Grid Model using Pandapower"""

import pandapower as pp
import numpy as np
import copy
from typing import Optional

# City coordinates for visualization
CITY_COORDS = {
    "Mumbai": {"lat": 19.076, "lon": 72.877},
    "Delhi": {"lat": 28.613, "lon": 77.209},
    "Bengaluru": {"lat": 12.971, "lon": 77.594},
    "Chennai": {"lat": 13.082, "lon": 80.270},
}

CITY_BUS_OFFSETS = {"Mumbai": 0, "Delhi": 100, "Bengaluru": 200, "Chennai": 300}


def _add_mumbai(net):
    """Mumbai grid: heavy industrial + coastal, thermal/solar/wind"""
    off = CITY_BUS_OFFSETS["Mumbai"]
    base = CITY_COORDS["Mumbai"]

    # Buses
    buses = {}
    bus_defs = [
        ("MUM_Slack", 220, "b", 0, 0),
        ("MUM_Sub1_HV", 220, "b", 0.05, 0.02),
        ("MUM_Sub1_LV", 33, "b", 0.05, 0.02),
        ("MUM_Sub2_HV", 220, "b", -0.04, 0.05),
        ("MUM_Sub2_LV", 33, "b", -0.04, 0.05),
        ("MUM_Sub3_HV", 220, "b", 0.03, -0.04),
        ("MUM_Sub3_LV", 33, "b", 0.03, -0.04),
        ("MUM_Sub4_HV", 110, "b", -0.06, -0.03),
        ("MUM_Sub4_LV", 33, "b", -0.06, -0.03),
        ("MUM_Solar", 33, "b", 0.08, 0.06),
        ("MUM_Wind", 33, "b", -0.09, 0.04),
        ("MUM_Thermal", 220, "b", 0.07, -0.05),
    ]
    for name, vn, zone, dlat, dlon in bus_defs:
        idx = pp.create_bus(net, vn_kv=vn, name=name, zone=zone,
                           geodata=(base["lat"] + dlat, base["lon"] + dlon))
        buses[name] = idx

    # External grid (slack)
    pp.create_ext_grid(net, buses["MUM_Slack"], vm_pu=1.02, name="MUM_Grid")

    # Generators
    pp.create_sgen(net, buses["MUM_Thermal"], p_mw=800, q_mvar=100, name="MUM_Thermal_Gen", type="Thermal")
    pp.create_sgen(net, buses["MUM_Solar"], p_mw=200, q_mvar=0, name="MUM_Solar_Farm", type="Solar")
    pp.create_sgen(net, buses["MUM_Wind"], p_mw=150, q_mvar=0, name="MUM_Wind_Farm", type="Wind")

    # Transformers
    pp.create_transformer(net, buses["MUM_Sub1_HV"], buses["MUM_Sub1_LV"],
                          std_type="63 MVA 110/20 kV", name="MUM_Trafo1")
    pp.create_transformer(net, buses["MUM_Sub2_HV"], buses["MUM_Sub2_LV"],
                          std_type="63 MVA 110/20 kV", name="MUM_Trafo2")
    pp.create_transformer(net, buses["MUM_Sub3_HV"], buses["MUM_Sub3_LV"],
                          std_type="63 MVA 110/20 kV", name="MUM_Trafo3")
    pp.create_transformer(net, buses["MUM_Sub4_HV"], buses["MUM_Sub4_LV"],
                          std_type="40 MVA 110/20 kV", name="MUM_Trafo4")

    # Lines (220kV backbone)
    line_type = "149-AL1/24-ST1A 110.0"
    pp.create_line(net, buses["MUM_Slack"], buses["MUM_Sub1_HV"], length_km=25, std_type=line_type, name="MUM_L1")
    pp.create_line(net, buses["MUM_Slack"], buses["MUM_Sub2_HV"], length_km=30, std_type=line_type, name="MUM_L2")
    pp.create_line(net, buses["MUM_Sub1_HV"], buses["MUM_Sub3_HV"], length_km=20, std_type=line_type, name="MUM_L3")
    pp.create_line(net, buses["MUM_Sub2_HV"], buses["MUM_Sub4_HV"], length_km=35, std_type=line_type, name="MUM_L4")
    pp.create_line(net, buses["MUM_Sub3_HV"], buses["MUM_Sub4_HV"], length_km=18, std_type=line_type, name="MUM_L5")
    pp.create_line(net, buses["MUM_Thermal"], buses["MUM_Slack"], length_km=40, std_type=line_type, name="MUM_L6")
    pp.create_line(net, buses["MUM_Solar"], buses["MUM_Sub1_LV"], length_km=15, std_type="94-AL1/15-ST1A 110.0", name="MUM_L7")
    pp.create_line(net, buses["MUM_Wind"], buses["MUM_Sub2_LV"], length_km=20, std_type="94-AL1/15-ST1A 110.0", name="MUM_L8")

    # Loads
    pp.create_load(net, buses["MUM_Sub1_LV"], p_mw=250, q_mvar=80, name="MUM_Residential_South")
    pp.create_load(net, buses["MUM_Sub2_LV"], p_mw=300, q_mvar=100, name="MUM_Industrial_West")
    pp.create_load(net, buses["MUM_Sub3_LV"], p_mw=200, q_mvar=60, name="MUM_Commercial_CBD")
    pp.create_load(net, buses["MUM_Sub4_LV"], p_mw=180, q_mvar=50, name="MUM_Residential_North")
    pp.create_load(net, buses["MUM_Sub3_LV"], p_mw=120, q_mvar=30, name="MUM_Critical_Hospitals")

    return buses


def _add_delhi(net):
    """Delhi grid: high demand, gas + thermal + solar"""
    off = CITY_BUS_OFFSETS["Delhi"]
    base = CITY_COORDS["Delhi"]

    buses = {}
    bus_defs = [
        ("DEL_Slack", 220, 0, 0),
        ("DEL_Sub1_HV", 220, 0.04, 0.03),
        ("DEL_Sub1_LV", 33, 0.04, 0.03),
        ("DEL_Sub2_HV", 220, -0.03, 0.04),
        ("DEL_Sub2_LV", 33, -0.03, 0.04),
        ("DEL_Sub3_HV", 110, 0.05, -0.03),
        ("DEL_Sub3_LV", 33, 0.05, -0.03),
        ("DEL_Thermal", 220, -0.06, -0.04),
        ("DEL_Gas", 220, 0.07, 0.05),
        ("DEL_Solar", 33, -0.08, 0.06),
    ]
    for name, vn, dlat, dlon in bus_defs:
        idx = pp.create_bus(net, vn_kv=vn, name=name,
                           geodata=(base["lat"] + dlat, base["lon"] + dlon))
        buses[name] = idx

    pp.create_ext_grid(net, buses["DEL_Slack"], vm_pu=1.02, name="DEL_Grid")

    pp.create_sgen(net, buses["DEL_Thermal"], p_mw=900, q_mvar=120, name="DEL_Thermal_Gen", type="Thermal")
    pp.create_sgen(net, buses["DEL_Gas"], p_mw=400, q_mvar=50, name="DEL_Gas_Gen", type="Gas")
    pp.create_sgen(net, buses["DEL_Solar"], p_mw=250, q_mvar=0, name="DEL_Solar_Farm", type="Solar")

    pp.create_transformer(net, buses["DEL_Sub1_HV"], buses["DEL_Sub1_LV"],
                          std_type="63 MVA 110/20 kV", name="DEL_Trafo1")
    pp.create_transformer(net, buses["DEL_Sub2_HV"], buses["DEL_Sub2_LV"],
                          std_type="63 MVA 110/20 kV", name="DEL_Trafo2")
    pp.create_transformer(net, buses["DEL_Sub3_HV"], buses["DEL_Sub3_LV"],
                          std_type="40 MVA 110/20 kV", name="DEL_Trafo3")

    line_type = "149-AL1/24-ST1A 110.0"
    pp.create_line(net, buses["DEL_Slack"], buses["DEL_Sub1_HV"], length_km=20, std_type=line_type, name="DEL_L1")
    pp.create_line(net, buses["DEL_Slack"], buses["DEL_Sub2_HV"], length_km=25, std_type=line_type, name="DEL_L2")
    pp.create_line(net, buses["DEL_Sub1_HV"], buses["DEL_Sub3_HV"], length_km=15, std_type=line_type, name="DEL_L3")
    pp.create_line(net, buses["DEL_Sub2_HV"], buses["DEL_Sub3_HV"], length_km=22, std_type=line_type, name="DEL_L4")
    pp.create_line(net, buses["DEL_Thermal"], buses["DEL_Slack"], length_km=35, std_type=line_type, name="DEL_L5")
    pp.create_line(net, buses["DEL_Gas"], buses["DEL_Sub1_HV"], length_km=28, std_type=line_type, name="DEL_L6")
    pp.create_line(net, buses["DEL_Solar"], buses["DEL_Sub2_LV"], length_km=18, std_type="94-AL1/15-ST1A 110.0", name="DEL_L7")

    pp.create_load(net, buses["DEL_Sub1_LV"], p_mw=350, q_mvar=110, name="DEL_Central_Delhi")
    pp.create_load(net, buses["DEL_Sub2_LV"], p_mw=280, q_mvar=90, name="DEL_South_Delhi")
    pp.create_load(net, buses["DEL_Sub3_LV"], p_mw=320, q_mvar=100, name="DEL_NCR_Industrial")

    return buses


def _add_bengaluru(net):
    """Bengaluru grid: IT corridor, solar/wind/hydro"""
    base = CITY_COORDS["Bengaluru"]
    buses = {}
    bus_defs = [
        ("BLR_Slack", 220, 0, 0),
        ("BLR_Sub1_HV", 110, 0.03, 0.02),
        ("BLR_Sub1_LV", 33, 0.03, 0.02),
        ("BLR_Sub2_HV", 110, -0.02, 0.04),
        ("BLR_Sub2_LV", 33, -0.02, 0.04),
        ("BLR_Sub3_HV", 110, 0.04, -0.03),
        ("BLR_Sub3_LV", 33, 0.04, -0.03),
        ("BLR_Solar", 33, 0.06, 0.05),
        ("BLR_Wind", 33, -0.05, -0.04),
        ("BLR_Hydro", 110, -0.07, 0.03),
    ]
    for name, vn, dlat, dlon in bus_defs:
        idx = pp.create_bus(net, vn_kv=vn, name=name,
                           geodata=(base["lat"] + dlat, base["lon"] + dlon))
        buses[name] = idx

    pp.create_ext_grid(net, buses["BLR_Slack"], vm_pu=1.02, name="BLR_Grid")
    pp.create_sgen(net, buses["BLR_Solar"], p_mw=300, q_mvar=0, name="BLR_Solar_Farm", type="Solar")
    pp.create_sgen(net, buses["BLR_Wind"], p_mw=180, q_mvar=0, name="BLR_Wind_Farm", type="Wind")
    pp.create_sgen(net, buses["BLR_Hydro"], p_mw=250, q_mvar=30, name="BLR_Hydro_Plant", type="Hydro")

    pp.create_transformer(net, buses["BLR_Sub1_HV"], buses["BLR_Sub1_LV"],
                          std_type="40 MVA 110/20 kV", name="BLR_Trafo1")
    pp.create_transformer(net, buses["BLR_Sub2_HV"], buses["BLR_Sub2_LV"],
                          std_type="40 MVA 110/20 kV", name="BLR_Trafo2")
    pp.create_transformer(net, buses["BLR_Sub3_HV"], buses["BLR_Sub3_LV"],
                          std_type="40 MVA 110/20 kV", name="BLR_Trafo3")

    line_type = "149-AL1/24-ST1A 110.0"
    lt2 = "94-AL1/15-ST1A 110.0"
    pp.create_line(net, buses["BLR_Slack"], buses["BLR_Sub1_HV"], length_km=18, std_type=lt2, name="BLR_L1")
    pp.create_line(net, buses["BLR_Slack"], buses["BLR_Sub2_HV"], length_km=22, std_type=lt2, name="BLR_L2")
    pp.create_line(net, buses["BLR_Sub1_HV"], buses["BLR_Sub3_HV"], length_km=15, std_type=lt2, name="BLR_L3")
    pp.create_line(net, buses["BLR_Sub2_HV"], buses["BLR_Sub3_HV"], length_km=20, std_type=lt2, name="BLR_L4")
    pp.create_line(net, buses["BLR_Hydro"], buses["BLR_Slack"], length_km=45, std_type=lt2, name="BLR_L5")
    pp.create_line(net, buses["BLR_Solar"], buses["BLR_Sub1_LV"], length_km=12, std_type=lt2, name="BLR_L6")
    pp.create_line(net, buses["BLR_Wind"], buses["BLR_Sub2_LV"], length_km=25, std_type=lt2, name="BLR_L7")

    pp.create_load(net, buses["BLR_Sub1_LV"], p_mw=220, q_mvar=70, name="BLR_IT_Corridor")
    pp.create_load(net, buses["BLR_Sub2_LV"], p_mw=180, q_mvar=50, name="BLR_Residential")
    pp.create_load(net, buses["BLR_Sub3_LV"], p_mw=160, q_mvar=45, name="BLR_Industrial")

    return buses


def _add_chennai(net):
    """Chennai grid: coastal, thermal/nuclear/wind"""
    base = CITY_COORDS["Chennai"]
    buses = {}
    bus_defs = [
        ("CHN_Slack", 220, 0, 0),
        ("CHN_Sub1_HV", 110, 0.03, -0.02),
        ("CHN_Sub1_LV", 33, 0.03, -0.02),
        ("CHN_Sub2_HV", 110, -0.03, 0.03),
        ("CHN_Sub2_LV", 33, -0.03, 0.03),
        ("CHN_Sub3_HV", 110, 0.05, 0.04),
        ("CHN_Sub3_LV", 33, 0.05, 0.04),
        ("CHN_Thermal", 220, -0.06, -0.05),
        ("CHN_Nuclear", 220, 0.08, -0.06),
        ("CHN_Wind", 33, -0.07, 0.05),
    ]
    for name, vn, dlat, dlon in bus_defs:
        idx = pp.create_bus(net, vn_kv=vn, name=name,
                           geodata=(base["lat"] + dlat, base["lon"] + dlon))
        buses[name] = idx

    pp.create_ext_grid(net, buses["CHN_Slack"], vm_pu=1.02, name="CHN_Grid")
    pp.create_sgen(net, buses["CHN_Thermal"], p_mw=600, q_mvar=80, name="CHN_Thermal_Gen", type="Thermal")
    pp.create_sgen(net, buses["CHN_Nuclear"], p_mw=500, q_mvar=60, name="CHN_Nuclear_Plant", type="Nuclear")
    pp.create_sgen(net, buses["CHN_Wind"], p_mw=200, q_mvar=0, name="CHN_Wind_Farm", type="Wind")

    pp.create_transformer(net, buses["CHN_Sub1_HV"], buses["CHN_Sub1_LV"],
                          std_type="40 MVA 110/20 kV", name="CHN_Trafo1")
    pp.create_transformer(net, buses["CHN_Sub2_HV"], buses["CHN_Sub2_LV"],
                          std_type="40 MVA 110/20 kV", name="CHN_Trafo2")
    pp.create_transformer(net, buses["CHN_Sub3_HV"], buses["CHN_Sub3_LV"],
                          std_type="40 MVA 110/20 kV", name="CHN_Trafo3")

    lt2 = "94-AL1/15-ST1A 110.0"
    line_type = "149-AL1/24-ST1A 110.0"
    pp.create_line(net, buses["CHN_Slack"], buses["CHN_Sub1_HV"], length_km=20, std_type=lt2, name="CHN_L1")
    pp.create_line(net, buses["CHN_Slack"], buses["CHN_Sub2_HV"], length_km=25, std_type=lt2, name="CHN_L2")
    pp.create_line(net, buses["CHN_Sub1_HV"], buses["CHN_Sub3_HV"], length_km=18, std_type=lt2, name="CHN_L3")
    pp.create_line(net, buses["CHN_Sub2_HV"], buses["CHN_Sub3_HV"], length_km=22, std_type=lt2, name="CHN_L4")
    pp.create_line(net, buses["CHN_Thermal"], buses["CHN_Slack"], length_km=38, std_type=line_type, name="CHN_L5")
    pp.create_line(net, buses["CHN_Nuclear"], buses["CHN_Slack"], length_km=50, std_type=line_type, name="CHN_L6")
    pp.create_line(net, buses["CHN_Wind"], buses["CHN_Sub2_LV"], length_km=15, std_type=lt2, name="CHN_L7")

    pp.create_load(net, buses["CHN_Sub1_LV"], p_mw=200, q_mvar=60, name="CHN_Industrial_Port")
    pp.create_load(net, buses["CHN_Sub2_LV"], p_mw=230, q_mvar=70, name="CHN_Residential")
    pp.create_load(net, buses["CHN_Sub3_LV"], p_mw=170, q_mvar=50, name="CHN_IT_Corridor")

    return buses


def create_national_grid():
    """Build the full 4-city national grid with inter-city corridors."""
    net = pp.create_empty_network(name="GRIDSENTINEL National Grid")

    city_buses = {}
    city_buses["Mumbai"] = _add_mumbai(net)
    city_buses["Delhi"] = _add_delhi(net)
    city_buses["Bengaluru"] = _add_bengaluru(net)
    city_buses["Chennai"] = _add_chennai(net)

    # Inter-city 400kV transmission corridors
    ic_type = "149-AL1/24-ST1A 110.0"
    pp.create_line(net, city_buses["Mumbai"]["MUM_Slack"], city_buses["Delhi"]["DEL_Slack"],
                   length_km=1400, std_type=ic_type, name="IC_Mumbai_Delhi")
    pp.create_line(net, city_buses["Delhi"]["DEL_Slack"], city_buses["Bengaluru"]["BLR_Slack"],
                   length_km=1740, std_type=ic_type, name="IC_Delhi_Bengaluru")
    pp.create_line(net, city_buses["Bengaluru"]["BLR_Slack"], city_buses["Chennai"]["CHN_Slack"],
                   length_km=350, std_type=ic_type, name="IC_Bengaluru_Chennai")
    pp.create_line(net, city_buses["Mumbai"]["MUM_Slack"], city_buses["Chennai"]["CHN_Slack"],
                   length_km=1340, std_type=ic_type, name="IC_Mumbai_Chennai")

    return net, city_buses


def run_powerflow(net):
    """Run AC power flow and return success status. Fallback to DC power flow."""
    try:
        pp.runpp(net, algorithm="nr", max_iteration=50, numba=False)
        return True
    except Exception:
        try:
            pp.rundcpp(net, numba=False)
            return True
        except Exception:
            return False


def get_grid_state(net, city_buses: dict) -> dict:
    """Extract full grid state as serializable dict."""
    success = run_powerflow(net)

    cities = []
    for city, buses in city_buses.items():
        city_bus_ids = list(buses.values())
        city_data = _extract_city_state(net, city, city_bus_ids)
        cities.append(city_data)

    total_gen = sum(c["total_generation_mw"] for c in cities)
    total_load = sum(c["total_load_mw"] for c in cities)
    avg_health = np.mean([c["health_score"] for c in cities]) if cities else 0

    state = {
        "converged": success,
        "cities": cities,
        "total_generation_mw": round(total_gen, 2),
        "total_load_mw": round(total_load, 2),
        "national_health_score": round(float(avg_health) if not np.isnan(avg_health) else 0.0, 2),
        "active_alerts": 0,
        "status": "healthy" if avg_health > 0.7 else "degraded" if avg_health > 0.4 else "critical",
    }

    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [clean_dict(v) for v in d]
        elif isinstance(d, float):
            return 0.0 if np.isnan(d) or np.isinf(d) else d
        return d

    return clean_dict(state)


def _extract_city_state(net, city: str, bus_ids: list) -> dict:
    """Extract state for a single city."""
    buses = []
    for idx in bus_ids:
        if idx in net.res_bus.index:
            row = net.bus.loc[idx]
            res = net.res_bus.loc[idx]
            geo_df = getattr(net, "bus_geodata", None)
            geo = geo_df.loc[idx] if geo_df is not None and idx in geo_df.index else None
            buses.append({
                "id": int(idx), "name": row["name"], "city": city,
                "voltage_pu": round(float(res["vm_pu"]), 4),
                "voltage_kv": round(float(row["vn_kv"] * res["vm_pu"]), 2),
                "type": str(row.get("type", "b")),
                "lat": float(geo["x"]) if geo is not None else 0,
                "lon": float(geo["y"]) if geo is not None else 0,
                "status": "normal" if 0.95 <= res["vm_pu"] <= 1.05 else "warning",
            })

    # Lines in this city
    lines = []
    for idx in net.line.index:
        if net.line.loc[idx, "from_bus"] in bus_ids or net.line.loc[idx, "to_bus"] in bus_ids:
            row = net.line.loc[idx]
            res = net.res_line.loc[idx] if idx in net.res_line.index else None
            loading = float(res["loading_percent"]) if res is not None else 0
            lines.append({
                "id": int(idx), "from_bus": int(row["from_bus"]), "to_bus": int(row["to_bus"]),
                "loading_percent": round(loading, 2),
                "p_from_mw": round(float(res["p_from_mw"]), 2) if res is not None else 0,
                "name": row["name"],
                "status": "normal" if loading < 80 else "warning" if loading < 100 else "critical",
                "city": city,
            })

    # Transformers
    trafos = []
    for idx in net.trafo.index:
        if net.trafo.loc[idx, "hv_bus"] in bus_ids or net.trafo.loc[idx, "lv_bus"] in bus_ids:
            row = net.trafo.loc[idx]
            res = net.res_trafo.loc[idx] if idx in net.res_trafo.index else None
            loading = float(res["loading_percent"]) if res is not None else 0
            temp = 65 + (loading / 100) * 35  # simplified thermal model
            trafos.append({
                "id": int(idx), "from_bus": int(row["hv_bus"]), "to_bus": int(row["lv_bus"]),
                "loading_percent": round(loading, 2),
                "temperature_c": round(temp, 1),
                "name": row["name"],
                "health_score": round(max(0, 1 - (loading / 120)), 2),
                "failure_probability": round(min(1, (loading / 100) ** 3 * 0.1), 4),
            })

    # Generators
    gens = []
    for idx in net.sgen.index:
        if net.sgen.loc[idx, "bus"] in bus_ids:
            row = net.sgen.loc[idx]
            res = net.res_sgen.loc[idx] if idx in net.res_sgen.index else None
            gens.append({
                "id": int(idx), "bus_id": int(row["bus"]),
                "name": row["name"], "type": row.get("type", "Unknown"),
                "capacity_mw": round(float(row["p_mw"]), 2),
                "output_mw": round(float(res["p_mw"]), 2) if res is not None else 0,
                "city": city,
            })

    total_gen = sum(g["output_mw"] for g in gens)
    total_load = sum(float(net.load.loc[i, "p_mw"]) for i in net.load.index if net.load.loc[i, "bus"] in bus_ids)
    total_losses = abs(total_gen - total_load) if total_gen > 0 else 0

    # Health score based on voltage deviations and line loadings
    v_scores = [1 - abs(b["voltage_pu"] - 1.0) * 10 for b in buses]
    l_scores = [max(0, 1 - l["loading_percent"] / 100) for l in lines]
    all_scores = v_scores + l_scores
    health = np.mean(all_scores) if all_scores else 1.0

    return {
        "city": city,
        "buses": buses, "lines": lines, "transformers": trafos, "generators": gens,
        "total_generation_mw": round(total_gen, 2),
        "total_load_mw": round(total_load, 2),
        "total_losses_mw": round(total_losses, 2),
        "health_score": round(float(np.clip(health, 0, 1)), 2),
        "status": "healthy" if health > 0.7 else "degraded" if health > 0.4 else "critical",
    }
