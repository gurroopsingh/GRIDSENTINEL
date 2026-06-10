"""GRIDSENTINEL — Pydantic Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Grid State ---
class BusState(BaseModel):
    id: int
    name: str
    city: str
    voltage_pu: float
    voltage_kv: float
    type: str  # slack, PV, PQ
    lat: float
    lon: float
    status: str = "normal"


class LineState(BaseModel):
    id: int
    from_bus: int
    to_bus: int
    loading_percent: float
    current_ka: float
    p_from_mw: float
    status: str = "normal"
    city: str = ""


class TransformerState(BaseModel):
    id: int
    from_bus: int
    to_bus: int
    loading_percent: float
    temperature_c: float = 65.0
    age_years: int = 10
    health_score: float = 1.0
    failure_probability: float = 0.0


class GeneratorState(BaseModel):
    id: int
    bus_id: int
    type: str
    fuel: str
    capacity_mw: float
    output_mw: float
    city: str


class CityGridState(BaseModel):
    city: str
    buses: list[BusState]
    lines: list[LineState]
    transformers: list[TransformerState]
    generators: list[GeneratorState]
    total_generation_mw: float
    total_load_mw: float
    total_losses_mw: float
    health_score: float
    status: str


class NationalGridState(BaseModel):
    timestamp: str
    cities: list[CityGridState]
    total_generation_mw: float
    total_load_mw: float
    national_health_score: float
    active_alerts: int
    status: str


# --- Alerts ---
class AlertCreate(BaseModel):
    city: str
    component_type: str
    component_id: str
    severity: str
    title: str
    message: str
    agent_source: str


class AlertResponse(BaseModel):
    id: str
    city: str
    severity: str
    title: str
    message: str
    agent_source: str
    resolved: bool
    created_at: datetime


# --- Agents ---
class AgentMessage(BaseModel):
    agent_name: str
    agent_role: str
    message: str
    reasoning: Optional[str] = None
    confidence: float = 0.0
    timestamp: str
    type: str = "analysis"  # analysis, challenge, defense, verdict


class DebateSession(BaseModel):
    session_id: str
    scenario: str
    rounds: list[list[AgentMessage]]
    verdict: Optional[AgentMessage] = None
    timestamp: str


# --- Simulation ---
class ScenarioRequest(BaseModel):
    scenario_name: str
    parameters: dict = {}
    custom_description: Optional[str] = None


class EconomicImpact(BaseModel):
    population_affected: int
    outage_duration_hours: float
    business_impact_crores: float
    prevention_cost_crores: float
    net_savings_crores: float
    critical_facilities: dict = {}
    jobs_at_risk: int = 0


class SimulationResult(BaseModel):
    id: str
    scenario_name: str
    cascade_timeline: list[dict]
    healing_actions: list[dict]
    economic_impact: EconomicImpact
    agent_debate: Optional[DebateSession] = None
    before_state: dict
    after_state: dict
    duration_seconds: float


# --- Future Grid ---
class FutureGridRequest(BaseModel):
    city: str
    target_year: int = 2035
    custom_prompt: Optional[str] = None


class FutureGridBlueprint(BaseModel):
    city: str
    target_year: int
    current_capacity_mw: float
    projected_demand_mw: float
    renewable_mix: dict
    new_infrastructure: list[dict]
    estimated_cost_crores: float
    resilience_improvement: float
    carbon_reduction_percent: float
    recommendations: list[str]
