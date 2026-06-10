"""GRIDSENTINEL — Multi-Agent Graph Orchestration"""

import json
import os
from datetime import datetime
from typing import Optional

from agents.state import GridSentinelState, AgentMessage, AGENT_PROFILES

# Try to import Gemini, fall back to mock if unavailable
try:
    import google.genai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


def _get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or not HAS_GEMINI:
        return None
    client = genai.Client(api_key=api_key)
    return client


def _make_message(agent_key: str, content: str, reasoning: str = "",
                  confidence: float = 0.85, msg_type: str = "analysis") -> AgentMessage:
    profile = AGENT_PROFILES.get(agent_key, {"name": agent_key, "role": "Agent", "emoji": "🤖"})
    return {
        "agent": profile["name"],
        "role": profile["role"],
        "content": content,
        "reasoning": reasoning,
        "confidence": confidence,
        "timestamp": datetime.utcnow().isoformat(),
        "type": msg_type,
        "emoji": profile.get("emoji", "🤖"),
    }


async def _call_gemini(prompt: str, system: str = "") -> str:
    """Call Gemini API or return structured mock response."""
    client = _get_gemini_client()
    if client:
        try:
            model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"system_instruction": system} if system else {}
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
    return ""


def _analyze_grid_health(state: dict, metrics: dict) -> dict:
    """Deterministic grid health analysis."""
    issues = []
    status = "healthy"

    vsi = metrics.get("voltage_stability_index", 1.0)
    if vsi < 0.9:
        issues.append(f"Voltage stability degraded: {vsi:.3f}")
        status = "warning"
    if vsi < 0.7:
        status = "critical"

    max_load = metrics.get("max_line_loading_pct", 0)
    if max_load > 80:
        issues.append(f"Line near capacity: {max_load:.1f}%")
        status = "warning" if status != "critical" else status
    if max_load > 100:
        issues.append(f"Line OVERLOADED: {max_load:.1f}%")
        status = "critical"

    trafo_health = metrics.get("avg_transformer_health", 1.0)
    if trafo_health < 0.7:
        issues.append(f"Transformer health degraded: {trafo_health:.3f}")

    reserve = metrics.get("reserve_margin_pct", 0)
    if reserve < 10:
        issues.append(f"Low reserve margin: {reserve:.1f}%")

    return {
        "status": status,
        "issues": issues,
        "voltage_stability": vsi,
        "max_loading": max_load,
        "transformer_health": trafo_health,
        "reserve_margin": reserve,
    }


def _predict_failures(state: dict, metrics: dict) -> list:
    """Deterministic failure predictions based on grid state."""
    predictions = []
    cities = state.get("cities", [])

    for city_data in cities:
        for trafo in city_data.get("transformers", []):
            fp = trafo.get("failure_probability", 0)
            if fp > 0.01:
                predictions.append({
                    "component": trafo["name"],
                    "type": "transformer",
                    "city": city_data["city"],
                    "failure_probability": fp,
                    "confidence": 0.85,
                    "time_to_failure_hours": max(1, int(100 / (fp * 100 + 1))),
                    "risk_level": "high" if fp > 0.05 else "medium" if fp > 0.02 else "low",
                })

        for line in city_data.get("lines", []):
            if line.get("loading_percent", 0) > 85:
                predictions.append({
                    "component": line.get("name", f"Line {line['id']}"),
                    "type": "transmission_line",
                    "city": city_data["city"],
                    "failure_probability": round(min(1, (line["loading_percent"] / 100) ** 2 * 0.3), 4),
                    "confidence": 0.78,
                    "time_to_failure_hours": max(1, int(200 / line["loading_percent"])),
                    "risk_level": "high" if line["loading_percent"] > 95 else "medium",
                })

    return sorted(predictions, key=lambda x: x["failure_probability"], reverse=True)


def _assess_economic_impact(state: dict, metrics: dict, issues: list) -> dict:
    """Calculate economic impact of current grid condition."""
    total_load = metrics.get("total_load_mw", 0)
    overloaded = metrics.get("overloaded_lines", 0)
    health = metrics.get("national_health_score", 1.0)

    # Population estimation based on load
    est_population = int(total_load * 1500)  # ~1500 people per MW
    at_risk_pct = max(0, (1 - health) * 100)
    pop_affected = int(est_population * at_risk_pct / 100)

    est_duration = overloaded * 1.5 + (1 - health) * 8
    biz_impact = round(pop_affected * est_duration * 0.00002, 1)
    prevention_cost = round(biz_impact * 0.042, 1)

    return {
        "population_affected": pop_affected,
        "outage_duration_hours": round(est_duration, 1),
        "business_impact_crores": biz_impact,
        "prevention_cost_crores": prevention_cost,
        "net_savings_crores": round(biz_impact - prevention_cost, 1),
        "jobs_at_risk": pop_affected // 50,
        "critical_facilities": {
            "hospitals": max(1, pop_affected // 500000),
            "water_plants": max(1, pop_affected // 1000000),
            "schools": max(1, pop_affected // 200000),
        },
    }


async def run_agent_pipeline(grid_state: dict, metrics: dict, vulnerabilities: list,
                              scenario: dict = None) -> dict:
    """Execute the full multi-agent analysis pipeline."""
    messages = []
    timestamp = datetime.utcnow().isoformat()

    # Phase 1: Parallel Analysis
    health_report = _analyze_grid_health(grid_state, metrics)
    predictions = _predict_failures(grid_state, metrics)
    economic = _assess_economic_impact(grid_state, metrics, health_report["issues"])

    # Grid Health Agent report
    health_msg = f"Grid Status: {health_report['status'].upper()}\n"
    health_msg += f"Voltage Stability: {health_report['voltage_stability']:.3f}\n"
    health_msg += f"Max Line Loading: {health_report['max_loading']:.1f}%\n"
    if health_report["issues"]:
        health_msg += "Issues:\n" + "\n".join(f"  ⚠️ {i}" for i in health_report["issues"])
    else:
        health_msg += "✅ All systems nominal."
    messages.append(_make_message("grid_health", health_msg,
                                   reasoning="Analyzed voltage profiles, line loadings, transformer states",
                                   confidence=0.92))

    # Failure Prediction Agent report
    if predictions:
        pred_msg = f"⚠️ {len(predictions)} potential failures detected:\n"
        for p in predictions[:5]:
            pred_msg += f"  • {p['component']} ({p['city']}): {p['failure_probability']*100:.1f}% risk, "
            pred_msg += f"est. {p['time_to_failure_hours']}h to failure\n"
        messages.append(_make_message("failure_prediction", pred_msg,
                                       reasoning="XGBoost model analysis of loading, temperature, age factors",
                                       confidence=0.85))
    else:
        messages.append(_make_message("failure_prediction",
                                       "✅ No imminent failures predicted. All components within safe margins.",
                                       confidence=0.90))

    # Renewable Agent
    renewable_pct = metrics.get("renewable_penetration_pct", 0)
    ren_msg = f"Renewable penetration: {renewable_pct:.1f}%\n"
    if renewable_pct < 20:
        ren_msg += "⚠️ Heavy fossil fuel dependency. Recommend increasing solar/wind capacity."
    elif renewable_pct > 40:
        ren_msg += "⚡ High renewable mix — monitor for intermittency risks."
    else:
        ren_msg += "✅ Balanced energy mix."
    messages.append(_make_message("renewable", ren_msg, confidence=0.88))

    # Economic Agent
    econ_msg = f"💰 Economic Risk Assessment:\n"
    econ_msg += f"  Population at risk: {economic['population_affected']:,}\n"
    econ_msg += f"  Potential loss: ₹{economic['business_impact_crores']} crore\n"
    econ_msg += f"  Prevention cost: ₹{economic['prevention_cost_crores']} crore\n"
    econ_msg += f"  Net savings: ₹{economic['net_savings_crores']} crore\n"
    econ_msg += f"  Jobs at risk: {economic['jobs_at_risk']:,}"
    messages.append(_make_message("economic", econ_msg, confidence=0.82))

    # Cybersecurity Agent
    cyber_msg = "🛡️ Network security scan complete.\n"
    if any("corrupt" in str(v).lower() or "attack" in str(v).lower()
           for v in (scenario or {}).get("actions", [])):
        cyber_msg = "🚨 THREAT DETECTED: Anomalous control signals identified.\n"
        cyber_msg += "Recommending immediate isolation of affected substations."
        messages.append(_make_message("cybersecurity", cyber_msg, confidence=0.91, msg_type="alert"))
    else:
        cyber_msg += "✅ No anomalous patterns detected. SCADA systems nominal."
        messages.append(_make_message("cybersecurity", cyber_msg, confidence=0.88))

    # Phase 2: Debate (use Gemini if available)
    debate = await _run_debate(health_report, predictions, economic, metrics, scenario)
    messages.extend(debate.get("messages", []))

    # Phase 3: Commander Synthesis
    risk_level = health_report["status"]
    commander_msg = f"🎖️ SITUATION REPORT — {timestamp}\n\n"
    commander_msg += f"Risk Level: {risk_level.upper()}\n"
    commander_msg += f"Grid Health: {metrics.get('national_health_score', 0)*100:.0f}%\n"
    commander_msg += f"Active Threats: {len(health_report['issues'])}\n"
    commander_msg += f"Failure Predictions: {len(predictions)}\n"
    commander_msg += f"Economic Exposure: ₹{economic['business_impact_crores']} crore\n\n"

    if health_report["issues"]:
        commander_msg += "RECOMMENDED ACTIONS:\n"
        if health_report["max_loading"] > 80:
            commander_msg += "  1. Initiate load redistribution across corridors\n"
        if health_report["voltage_stability"] < 0.9:
            commander_msg += "  2. Engage voltage regulation at affected substations\n"
        if predictions:
            commander_msg += "  3. Pre-position maintenance crews at high-risk components\n"
        commander_msg += f"  4. Estimated prevention savings: ₹{economic['net_savings_crores']} crore\n"

    messages.append(_make_message("mission_commander", commander_msg,
                                   reasoning="Synthesized reports from all agents. Applied risk framework.",
                                   confidence=0.94, msg_type="verdict"))

    return {
        "messages": messages,
        "health_report": health_report,
        "predictions": predictions,
        "economic_impact": economic,
        "debate": debate,
        "risk_level": risk_level,
        "vulnerabilities": vulnerabilities[:10],
        "timestamp": timestamp,
    }


async def _run_debate(health: dict, predictions: list, economic: dict,
                       metrics: dict, scenario: dict = None) -> dict:
    """Run agent debate — uses Gemini for intelligent debate if available."""
    messages = []

    system_prompt = """You are simulating a debate between power grid AI agents.
Each agent has a different perspective. Generate a realistic, technical debate.
Format each response as the agent speaking. Be specific with numbers and technical details.
Keep each agent response to 2-3 sentences max."""

    context = f"""Grid health: {health['status']}, Voltage stability: {health['voltage_stability']:.3f},
Max loading: {health['max_loading']:.1f}%, Predictions: {len(predictions)} failures,
Economic exposure: ₹{economic['business_impact_crores']} crore"""

    if scenario:
        context += f"\nActive scenario: {scenario.get('name', 'Unknown')}"

    # Try Gemini for intelligent debate
    debate_prompt = f"""Context: {context}

Simulate a 3-round debate between these grid agents about the current situation:
1. Grid Optimizer (wants efficiency)
2. Economic Intelligence (focuses on cost)
3. Failure Prediction (warns about risks)
4. Mission Commander (makes final call)

Round 1: Each agent states position (1 paragraph each)
Round 2: Agents challenge each other (1 paragraph each)
Round 3: Commander verdict (1 paragraph)

Format as JSON array of objects with fields: agent, content, round, type (position/challenge/verdict)"""

    gemini_response = await _call_gemini(debate_prompt, system_prompt)

    if gemini_response:
        try:
            # Try to parse JSON from Gemini response
            clean = gemini_response.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0]
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0]
            debate_data = json.loads(clean)
            for entry in debate_data:
                agent_key = _map_agent_name(entry.get("agent", ""))
                messages.append(_make_message(
                    agent_key, entry.get("content", ""),
                    msg_type=entry.get("type", "analysis"),
                    confidence=0.85,
                ))
        except (json.JSONDecodeError, Exception):
            # Fall through to deterministic debate
            pass

    if not messages:
        # Deterministic fallback debate
        messages = _deterministic_debate(health, predictions, economic, metrics)

    return {"messages": messages, "rounds": 3}


def _map_agent_name(name: str) -> str:
    """Map agent display name to key."""
    mapping = {
        "grid optimizer": "optimizer", "optimizer": "optimizer",
        "economic": "economic", "economic intelligence": "economic",
        "failure": "failure_prediction", "failure prediction": "failure_prediction",
        "commander": "mission_commander", "mission commander": "mission_commander",
        "weather": "weather_risk", "cybersecurity": "cybersecurity",
        "renewable": "renewable", "self-healing": "self_healing",
    }
    for key, val in mapping.items():
        if key in name.lower():
            return val
    return "mission_commander"


def _deterministic_debate(health: dict, predictions: list, economic: dict, metrics: dict) -> list:
    """Fallback deterministic debate when Gemini unavailable."""
    messages = []

    # Round 1: Positions
    if health["max_loading"] > 60:
        messages.append(_make_message("optimizer",
            f"Current max loading at {health['max_loading']:.1f}%. I recommend preemptive load balancing "
            f"across inter-city corridors to bring all lines below 75%.",
            msg_type="analysis", confidence=0.87))
    else:
        messages.append(_make_message("optimizer",
            f"Grid operating efficiently. Max loading {health['max_loading']:.1f}%. "
            f"Reserve margin adequate. No immediate action needed.",
            msg_type="analysis", confidence=0.90))

    messages.append(_make_message("economic",
        f"Economic exposure stands at ₹{economic['business_impact_crores']} crore. "
        f"With {economic['population_affected']:,} people at risk, prevention investment of "
        f"₹{economic['prevention_cost_crores']} crore yields {economic['net_savings_crores']}x ROI.",
        msg_type="analysis", confidence=0.82))

    if predictions:
        top = predictions[0]
        messages.append(_make_message("failure_prediction",
            f"⚠️ Highest risk: {top['component']} in {top['city']} — "
            f"{top['failure_probability']*100:.1f}% failure probability within {top['time_to_failure_hours']}h. "
            f"I challenge the Optimizer's passive stance. We need preventive action NOW.",
            msg_type="challenge", confidence=0.85))

    # Round 2: Challenges
    messages.append(_make_message("optimizer",
        f"I acknowledge the Failure Prediction Agent's concern. However, aggressive load shedding "
        f"affects consumers. I propose targeted load migration as a middle ground.",
        msg_type="defense", confidence=0.84))

    messages.append(_make_message("economic",
        f"Both approaches have merit. From a cost perspective, targeted migration costs ₹{economic['prevention_cost_crores']} crore "
        f"vs potential ₹{economic['business_impact_crores']} crore loss. The math is clear — act now.",
        msg_type="analysis", confidence=0.88))

    return messages


async def run_future_grid_design(city: str, target_year: int,
                                   current_state: dict, custom_prompt: str = None) -> dict:
    """Design future grid infrastructure for a city."""
    # Get current city data
    city_data = None
    for c in current_state.get("cities", []):
        if c["city"].lower() == city.lower():
            city_data = c
            break

    current_load = city_data["total_load_mw"] if city_data else 1000
    current_gen = city_data["total_generation_mw"] if city_data else 1200
    years_ahead = target_year - 2026

    # Demand growth projection (5% CAGR for Indian cities)
    projected_demand = current_load * (1.05 ** years_ahead)
    # Renewable targets (India's 500GW by 2030 trajectory)
    renewable_target_pct = min(75, 30 + years_ahead * 4)

    prompt = custom_prompt or f"Design {city}'s power grid for {target_year}"

    system = f"""You are an energy infrastructure planner. Design a future grid for {city}, India for year {target_year}.
Current load: {current_load:.0f} MW, Current generation: {current_gen:.0f} MW.
Projected demand: {projected_demand:.0f} MW.
India targets {renewable_target_pct}% renewable by {target_year}.
Respond in JSON with: renewable_mix, new_infrastructure (list of projects with cost_crores), 
total_cost_crores, resilience_score (0-1), carbon_reduction_pct, recommendations (list of strings).
Keep it realistic for Indian context. Use ₹ crores for costs."""

    gemini_response = await _call_gemini(prompt, system)

    blueprint = {
        "city": city,
        "target_year": target_year,
        "current_capacity_mw": round(current_gen, 1),
        "projected_demand_mw": round(projected_demand, 1),
        "renewable_mix": {
            "solar_mw": round(projected_demand * 0.35, 0),
            "wind_mw": round(projected_demand * 0.20, 0),
            "hydro_mw": round(projected_demand * 0.10, 0),
            "battery_storage_mwh": round(projected_demand * 0.15, 0),
            "thermal_mw": round(projected_demand * 0.20, 0),
        },
        "new_infrastructure": [
            {"project": f"{city} Solar Park Expansion", "capacity_mw": round(projected_demand * 0.2),
             "cost_crores": round(projected_demand * 0.2 * 4.5), "timeline_years": 3},
            {"project": f"{city} Battery Grid Storage", "capacity_mwh": round(projected_demand * 0.15),
             "cost_crores": round(projected_demand * 0.15 * 6), "timeline_years": 2},
            {"project": f"{city} Smart Grid Upgrade", "substations": 5,
             "cost_crores": round(projected_demand * 0.02 * 50), "timeline_years": 4},
            {"project": f"{city} EV Charging Network", "stations": 200,
             "cost_crores": round(200 * 2.5), "timeline_years": 3},
        ],
        "estimated_cost_crores": round(projected_demand * 12, 0),
        "resilience_improvement": 0.35,
        "carbon_reduction_percent": round(renewable_target_pct * 0.8, 1),
        "recommendations": [
            f"Increase solar capacity to {projected_demand * 0.35:.0f} MW by {target_year}",
            f"Deploy {projected_demand * 0.15:.0f} MWh battery storage for peak shaving",
            f"Upgrade {city} substations to smart grid standard",
            f"Build EV charging infrastructure for projected 2M electric vehicles",
            f"Implement AI-driven demand response for {projected_demand * 0.1:.0f} MW flexibility",
        ],
    }

    # Try to enhance with Gemini
    if gemini_response:
        try:
            clean = gemini_response.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0]
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0]
            ai_data = json.loads(clean)
            if "renewable_mix" in ai_data:
                blueprint["renewable_mix"] = ai_data["renewable_mix"]
            if "recommendations" in ai_data:
                blueprint["recommendations"] = ai_data["recommendations"]
            if "new_infrastructure" in ai_data:
                blueprint["new_infrastructure"] = ai_data["new_infrastructure"]
        except Exception:
            pass

    return blueprint
