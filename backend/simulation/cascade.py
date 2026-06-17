"""GRIDSENTINEL-X Ω — Cascading Failure Simulator"""

import networkx as nx
import numpy as np
import copy
from datetime import datetime, timedelta
from simulation.grid_model import run_powerflow


def build_topology_graph(net) -> nx.Graph:
    """Build NetworkX graph from pandapower network for cascade analysis."""
    G = nx.Graph()

    for idx in net.bus.index:
        row = net.bus.loc[idx]
        G.add_node(int(idx), name=row["name"], vn_kv=row["vn_kv"], type="bus")

    for idx in net.line.index:
        row = net.line.loc[idx]
        if row["in_service"]:
            G.add_edge(int(row["from_bus"]), int(row["to_bus"]),
                       key=f"line_{idx}", type="line", name=row["name"],
                       length_km=row["length_km"])

    for idx in net.trafo.index:
        row = net.trafo.loc[idx]
        if row["in_service"]:
            G.add_edge(int(row["hv_bus"]), int(row["lv_bus"]),
                       key=f"trafo_{idx}", type="trafo", name=row["name"])

    return G


def simulate_cascade(net, initial_failure: dict, max_steps: int = 10) -> list:
    """Simulate cascading failure from an initial failure event.
    
    Returns timeline of cascade events.
    """
    cascade_net = copy.deepcopy(net)
    timeline = []
    t = datetime.utcnow()

    # Apply initial failure
    event = _apply_failure(cascade_net, initial_failure, t)
    timeline.append(event)

    for step in range(max_steps):
        t += timedelta(seconds=30)
        success = run_powerflow(cascade_net)

        if not success:
            timeline.append({
                "step": step + 1, "time": t.isoformat(),
                "event": "powerflow_divergence",
                "description": "Power flow failed to converge — system collapse",
                "severity": "emergency",
            })
            break

        # Check for overloaded lines
        new_failures = []
        for idx in cascade_net.line.index:
            if not cascade_net.line.loc[idx, "in_service"]:
                continue
            if idx in cascade_net.res_line.index:
                loading = cascade_net.res_line.loc[idx, "loading_percent"]
                if loading > 120:
                    new_failures.append({
                        "type": "line_overload",
                        "component": "line",
                        "index": int(idx),
                        "name": cascade_net.line.loc[idx, "name"],
                        "loading": round(float(loading), 1),
                    })

        # Check for overloaded transformers
        for idx in cascade_net.trafo.index:
            if not cascade_net.trafo.loc[idx, "in_service"]:
                continue
            if idx in cascade_net.res_trafo.index:
                loading = cascade_net.res_trafo.loc[idx, "loading_percent"]
                if loading > 130:
                    new_failures.append({
                        "type": "trafo_overload",
                        "component": "trafo",
                        "index": int(idx),
                        "name": cascade_net.trafo.loc[idx, "name"],
                        "loading": round(float(loading), 1),
                    })

        # Check voltage collapse
        for idx in cascade_net.res_bus.index:
            vm = cascade_net.res_bus.loc[idx, "vm_pu"]
            if vm < 0.85 or vm > 1.15:
                new_failures.append({
                    "type": "voltage_violation",
                    "component": "bus",
                    "index": int(idx),
                    "name": cascade_net.bus.loc[idx, "name"],
                    "voltage_pu": round(float(vm), 4),
                })

        if not new_failures:
            timeline.append({
                "step": step + 1, "time": t.isoformat(),
                "event": "cascade_stopped",
                "description": "System stabilized — no further failures",
                "severity": "info",
            })
            break

        # Trip overloaded components
        for failure in new_failures:
            if failure["component"] == "line":
                cascade_net.line.loc[failure["index"], "in_service"] = False
            elif failure["component"] == "trafo":
                cascade_net.trafo.loc[failure["index"], "in_service"] = False

            timeline.append({
                "step": step + 1, "time": t.isoformat(),
                "event": failure["type"],
                "component": failure["name"],
                "description": f"{failure['name']} tripped — {failure['type']}",
                "severity": "critical",
                "details": failure,
            })

    return timeline


def _apply_failure(net, failure: dict, t) -> dict:
    """Apply initial failure and return event dict."""
    f_type = failure.get("type", "line")
    name = failure.get("name", "")

    if f_type == "line":
        mask = net.line["name"] == name
        net.line.loc[mask, "in_service"] = False
    elif f_type == "trafo":
        mask = net.trafo["name"] == name
        net.trafo.loc[mask, "in_service"] = False
    elif f_type == "generator":
        mask = net.sgen["name"] == name
        net.sgen.loc[mask, "in_service"] = False

    return {
        "step": 0, "time": t.isoformat(),
        "event": f"initial_{f_type}_failure",
        "component": name,
        "description": f"Initial failure: {name} taken offline",
        "severity": "emergency",
    }


def identify_vulnerable_paths(net) -> list:
    """Identify N-1 contingency vulnerabilities."""
    G = build_topology_graph(net)
    vulnerabilities = []

    # Find bridges (single points of failure)
    bridges = list(nx.bridges(G))
    for u, v in bridges:
        u_name = G.nodes[u].get("name", str(u))
        v_name = G.nodes[v].get("name", str(v))
        vulnerabilities.append({
            "type": "bridge",
            "from": u_name, "to": v_name,
            "risk": "high",
            "description": f"Single point of failure between {u_name} and {v_name}",
        })

    # Find articulation points
    ap = list(nx.articulation_points(G))
    for node in ap:
        name = G.nodes[node].get("name", str(node))
        vulnerabilities.append({
            "type": "articulation_point",
            "bus": name,
            "risk": "critical",
            "description": f"Bus {name} is a critical junction — failure isolates subgraph",
        })

    return vulnerabilities
