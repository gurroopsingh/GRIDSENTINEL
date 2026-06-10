"""GRIDSENTINEL — Database Models"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db.connection import Base


def gen_uuid():
    return str(uuid.uuid4())


class GridNetwork(Base):
    __tablename__ = "grid_networks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(50))
    region: Mapped[str] = mapped_column(String(50))
    total_buses: Mapped[int] = mapped_column(Integer, default=0)
    total_capacity_mw: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="healthy")
    topology_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    city: Mapped[str] = mapped_column(String(50))
    component_type: Mapped[str] = mapped_column(String(50))
    component_id: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(20))  # info, warning, critical, emergency
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    agent_source: Mapped[str] = mapped_column(String(50))
    agent_reasoning: Mapped[dict] = mapped_column(JSON, default=dict)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentDecision(Base):
    __tablename__ = "agent_decisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    agent_name: Mapped[str] = mapped_column(String(50))
    action_type: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50), nullable=True)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[str] = mapped_column(Text)
    action_taken: Mapped[dict] = mapped_column(JSON, default=dict)
    outcome: Mapped[str] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DebateEntry(Base):
    __tablename__ = "debate_entries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(String(36))
    agent_name: Mapped[str] = mapped_column(String(50))
    round_number: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    challenges: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    scenario_name: Mapped[str] = mapped_column(String(100))
    scenario_type: Mapped[str] = mapped_column(String(50))
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    initial_state: Mapped[dict] = mapped_column(JSON, default=dict)
    final_state: Mapped[dict] = mapped_column(JSON, default=dict)
    agent_actions: Mapped[dict] = mapped_column(JSON, default=list)
    economic_impact: Mapped[dict] = mapped_column(JSON, default=dict)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LearningMemory(Base):
    __tablename__ = "learning_memory"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    event_type: Mapped[str] = mapped_column(String(50))
    pattern: Mapped[str] = mapped_column(Text)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    times_validated: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
