"""GRIDSENTINEL — FastAPI Application"""

import asyncio
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from simulation.grid_model import create_national_grid, get_grid_state, run_powerflow
from simulation.scenarios import SCENARIOS, apply_scenario, parse_custom_scenario
from simulation.cascade import simulate_cascade, identify_vulnerable_paths
from simulation.self_heal import execute_healing
from simulation.metrics import calculate_metrics

# Global state
grid_net = None
city_buses = None
current_state = None
ws_clients: list[WebSocket] = []
alert_log: list[dict] = []
agent_log: list[dict] = []
debate_log: list[dict] = []
simulation_history: list[dict] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global grid_net, city_buses, current_state
    print("⚡ GRIDSENTINEL — Initializing National Grid...")
    grid_net, city_buses = create_national_grid()
    success = run_powerflow(grid_net)
    current_state = get_grid_state(grid_net, city_buses)
    print(f"✅ Grid initialized: {len(grid_net.bus)} buses, {len(grid_net.line)} lines, converged={success}")
    # Start background simulation tick
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()


app = FastAPI(title="GRIDSENTINEL", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
                   allow_credentials=True)


async def simulation_loop():
    """Background loop — tick grid state every N seconds."""
    settings = get_settings()
    while True:
        await asyncio.sleep(settings.simulation_tick_seconds)
        global current_state
        try:
            current_state = get_grid_state(grid_net, city_buses)
            metrics = calculate_metrics(current_state)
            payload = json.dumps({
                "type": "grid_update",
                "data": {**current_state, "metrics": metrics},
                "timestamp": datetime.utcnow().isoformat(),
            }, default=str)
            for ws in ws_clients[:]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    ws_clients.remove(ws)
        except Exception as e:
            print(f"Simulation tick error: {e}")


async def broadcast(event_type: str, data: dict):
    """Broadcast event to all WebSocket clients."""
    payload = json.dumps({"type": event_type, "data": data,
                          "timestamp": datetime.utcnow().isoformat()}, default=str)
    for ws in ws_clients[:]:
        try:
            await ws.send_text(payload)
        except Exception:
            ws_clients.remove(ws)


# ─── WebSocket ───
@app.websocket("/ws/grid")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.append(websocket)
    try:
        # Send initial state
        metrics = calculate_metrics(current_state) if current_state else {}
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "data": {**(current_state or {}), "metrics": metrics},
            "timestamp": datetime.utcnow().isoformat(),
        }, default=str))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_clients.remove(websocket)


# ─── Grid State ───
@app.get("/api/grid/state")
async def get_state():
    return current_state or {}


@app.get("/api/grid/metrics")
async def get_metrics():
    if not current_state:
        return {}
    return calculate_metrics(current_state)


@app.get("/api/grid/topology")
async def get_topology():
    """Return topology for 3D visualization."""
    if not grid_net or not city_buses:
        return {}
    nodes = []
    edges = []
    for city, buses in city_buses.items():
        for name, idx in buses.items():
            geo = grid_net.bus_geodata.loc[idx] if idx in grid_net.bus_geodata.index else None
            nodes.append({
                "id": int(idx), "name": name, "city": city,
                "vn_kv": float(grid_net.bus.loc[idx, "vn_kv"]),
                "lat": float(geo["x"]) if geo is not None else 0,
                "lon": float(geo["y"]) if geo is not None else 0,
                "type": "substation" if "Sub" in name else "generator" if any(
                    t in name for t in ["Solar", "Wind", "Thermal", "Gas", "Hydro", "Nuclear"]
                ) else "slack" if "Slack" in name else "bus",
            })
    for idx in grid_net.line.index:
        row = grid_net.line.loc[idx]
        is_intercity = row["name"].startswith("IC_")
        edges.append({
            "id": int(idx), "from": int(row["from_bus"]), "to": int(row["to_bus"]),
            "name": row["name"], "type": "intercity" if is_intercity else "transmission",
            "length_km": float(row["length_km"]),
            "in_service": bool(row["in_service"]),
        })
    return {"nodes": nodes, "edges": edges}


@app.get("/api/grid/vulnerabilities")
async def get_vulnerabilities():
    if not grid_net:
        return []
    return identify_vulnerable_paths(grid_net)


# ─── Scenarios ───
@app.get("/api/scenarios")
async def list_scenarios():
    return {k: {"name": v["name"], "description": v["description"],
                "type": v["type"], "severity": v["severity"], "city": v["city"]}
            for k, v in SCENARIOS.items()}


@app.post("/api/simulation/run")
async def run_simulation(scenario_key: str = Query(...), custom_description: Optional[str] = None):
    """Run a disaster scenario simulation."""
    import copy as cp

    if scenario_key == "custom" and custom_description:
        scenario_def = parse_custom_scenario(custom_description)
        affected_net = cp.deepcopy(grid_net)
        for action in scenario_def["actions"]:
            from simulation.scenarios import _apply_action
            _apply_action(affected_net, city_buses, action, scenario_def["city"])
    else:
        affected_net, scenario_def = apply_scenario(grid_net, city_buses, scenario_key)

    # Get before state
    before_state = get_grid_state(grid_net, city_buses)
    before_metrics = calculate_metrics(before_state)

    # Run power flow on affected network
    run_powerflow(affected_net)
    after_state = get_grid_state(affected_net, city_buses)
    after_metrics = calculate_metrics(after_state)

    # Simulate cascade
    cascade_timeline = []
    if scenario_def.get("severity") in ("critical", "emergency"):
        initial_failure = {}
        for action in scenario_def.get("actions", []):
            if action["type"] in ("disable_line", "disable_trafo"):
                targets = action.get("targets", [])
                if targets:
                    f_type = "line" if "line" in action["type"] else "trafo"
                    initial_failure = {"type": f_type, "name": targets[0]}
                    break
        if initial_failure:
            cascade_timeline = simulate_cascade(affected_net, initial_failure)

    # Self-healing
    healing_result = execute_healing(affected_net, city_buses, {"scenario": scenario_def})

    # Economic impact calculation
    pop = scenario_def.get("expected_impact", {}).get("population", 2000000)
    duration = scenario_def.get("expected_impact", {}).get("duration_hours", 6)
    biz_impact = round(pop * duration * 0.00002, 1)  # ₹ crore estimate
    prevention_cost = round(biz_impact * 0.04, 1)

    result = {
        "id": str(uuid.uuid4()),
        "scenario": scenario_def["name"],
        "scenario_key": scenario_key,
        "description": scenario_def["description"],
        "severity": scenario_def["severity"],
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "cascade_timeline": cascade_timeline,
        "healing_result": healing_result,
        "economic_impact": {
            "population_affected": pop,
            "outage_duration_hours": duration,
            "business_impact_crores": biz_impact,
            "prevention_cost_crores": prevention_cost,
            "net_savings_crores": round(biz_impact - prevention_cost, 1),
            "critical_facilities": {"hospitals": pop // 500000, "water_plants": pop // 1000000 + 1},
            "jobs_at_risk": pop // 50,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    simulation_history.append(result)
    await broadcast("simulation_result", result)
    return result


# ─── Agents ───
@app.get("/api/agents/log")
async def get_agent_log():
    return agent_log[-50:]


@app.get("/api/agents/debate")
async def get_debate_log():
    return debate_log[-10:]


@app.post("/api/agents/analyze")
async def trigger_analysis():
    """Trigger multi-agent analysis of current grid state."""
    if not current_state:
        return {"error": "Grid not initialized"}

    metrics = calculate_metrics(current_state)
    vulnerabilities = identify_vulnerable_paths(grid_net)

    # Run agent analysis (will be enhanced with Gemini in Phase 3)
    from agents.graph import run_agent_pipeline
    result = await run_agent_pipeline(current_state, metrics, vulnerabilities)

    agent_log.extend(result.get("messages", []))
    if result.get("debate"):
        debate_log.append(result["debate"])

    await broadcast("agent_analysis", result)
    return result


# ─── Future Grid ───
@app.post("/api/future-grid/design")
async def design_future_grid(city: str = Query("Mumbai"), target_year: int = Query(2035),
                              prompt: Optional[str] = None):
    """Design future grid infrastructure."""
    from agents.graph import run_future_grid_design
    result = await run_future_grid_design(city, target_year, current_state, prompt)
    await broadcast("future_grid_result", result)
    return result


# ─── Alerts ───
@app.get("/api/alerts")
async def get_alerts(limit: int = 50):
    return alert_log[-limit:]


# ─── History ───
@app.get("/api/simulation/history")
async def get_simulation_history():
    return simulation_history[-20:]


# ─── Health ───
@app.get("/api/health")
async def health():
    return {
        "status": "operational",
        "grid_initialized": grid_net is not None,
        "buses": len(grid_net.bus) if grid_net else 0,
        "lines": len(grid_net.line) if grid_net else 0,
        "ws_clients": len(ws_clients),
    }
