"""GRIDSENTINEL — Agent Shared State"""

from typing import TypedDict, Annotated, Optional
from datetime import datetime
import operator


class AgentMessage(TypedDict):
    agent: str
    role: str
    content: str
    reasoning: str
    confidence: float
    timestamp: str
    type: str  # analysis, challenge, defense, verdict, action


class GridSentinelState(TypedDict):
    # Input context
    grid_state: dict
    metrics: dict
    vulnerabilities: list
    scenario: Optional[dict]

    # Agent communication
    messages: Annotated[list[AgentMessage], operator.add]

    # Analysis results from each agent
    grid_health_report: Optional[dict]
    failure_predictions: Optional[list]
    weather_assessment: Optional[dict]
    renewable_status: Optional[dict]
    economic_analysis: Optional[dict]
    cyber_assessment: Optional[dict]
    optimization_plan: Optional[dict]
    healing_actions: Optional[list]

    # Debate
    debate_rounds: Optional[list]
    debate_verdict: Optional[dict]

    # Final outputs
    situation_report: Optional[str]
    recommended_actions: Optional[list]
    risk_level: Optional[str]

    # Learning
    patterns_discovered: Optional[list]


AGENT_PROFILES = {
    "mission_commander": {
        "name": "Mission Commander",
        "role": "Chief Coordinator",
        "emoji": "🎖️",
        "description": "Orchestrates all agents. Makes final decisions.",
    },
    "grid_health": {
        "name": "Grid Health Agent",
        "role": "Infrastructure Monitor",
        "emoji": "🏥",
        "description": "Monitors bus voltages, line loadings, transformer health.",
    },
    "failure_prediction": {
        "name": "Failure Prediction Agent",
        "role": "Predictive Analyst",
        "emoji": "🔮",
        "description": "Predicts component failures using ML models.",
    },
    "weather_risk": {
        "name": "Weather Risk Agent",
        "role": "Climate Analyst",
        "emoji": "🌪️",
        "description": "Assesses weather impact on grid infrastructure.",
    },
    "renewable": {
        "name": "Renewable Optimizer",
        "role": "Clean Energy Specialist",
        "emoji": "☀️",
        "description": "Optimizes solar, wind, hydro, battery integration.",
    },
    "economic": {
        "name": "Economic Intelligence",
        "role": "Financial Analyst",
        "emoji": "💰",
        "description": "Calculates economic impact in ₹ crores.",
    },
    "cybersecurity": {
        "name": "Cybersecurity Agent",
        "role": "Threat Hunter",
        "emoji": "🛡️",
        "description": "Detects anomalies, identifies attack patterns.",
    },
    "optimizer": {
        "name": "Grid Optimizer",
        "role": "Operations Researcher",
        "emoji": "⚡",
        "description": "Optimizes grid operations and load distribution.",
    },
    "self_healing": {
        "name": "Self-Healing Agent",
        "role": "Autonomous Responder",
        "emoji": "🔧",
        "description": "Executes autonomous healing actions.",
    },
    "emergency": {
        "name": "Emergency Response",
        "role": "Crisis Manager",
        "emoji": "🚨",
        "description": "Manages emergency protocols and escalation.",
    },
    "energy_scientist": {
        "name": "Energy Scientist",
        "role": "Research Analyst",
        "emoji": "🔬",
        "description": "Discovers hidden patterns. Generates hypotheses.",
    },
}
