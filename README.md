# ⚡ GRIDSENTINEL-X Ω

### The World's First Autonomous Multi-Agent Energy Defense and Infrastructure Planning System

![Status](https://img.shields.io/badge/Status-Active-00ff88?style=flat-square)
![Agents](https://img.shields.io/badge/Agents-12%20Online-00d4ff?style=flat-square)
![Cities](https://img.shields.io/badge/Coverage-4%20Cities-8b5cf6?style=flat-square)
![AI](https://img.shields.io/badge/AI-Gemini%20Powered-ff3366?style=flat-square)

---

## 🎯 What is GRIDSENTINEL-X Ω?

An **AI-native autonomous infrastructure platform** that predicts, simulates, prevents, and self-heals power grid failures before they occur. Built with multi-agent AI, real-time digital twin simulation, and autonomous decision-making.

**Not a monitoring dashboard. An autonomous defense system.**

---

## 🏗️ Architecture

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js, Three.js, Tailwind, Framer Motion | NASA-style Mission Control UI |
| **Backend** | FastAPI, WebSocket, Redis | Real-time API & streaming |
| **AI Brain** | LangGraph, Gemini API | 12 autonomous agents |
| **Simulation** | Pandapower, NetworkX | 4-city digital twin |
| **Database** | PostgreSQL | Persistent storage |

---

## 🤖 Multi-Agent System

| Agent | Role |
|-------|------|
| 🎖️ Mission Commander | Orchestrates all agents, makes final decisions |
| 🏥 Grid Health | Monitors voltages, loadings, transformer states |
| 🔮 Failure Prediction | XGBoost-powered failure probability estimation |
| 🌪️ Weather Risk | Climate impact on infrastructure |
| ☀️ Renewable Optimizer | Solar/wind/battery balancing |
| 💰 Economic Intelligence | ₹ crore impact calculations |
| 🛡️ Cybersecurity | Anomaly detection, threat hunting |
| ⚡ Grid Optimizer | Load distribution optimization |
| 🔧 Self-Healing | Autonomous repair actions |
| 🚨 Emergency Response | Crisis management protocols |
| 🔬 Energy Scientist | Pattern discovery, hypothesis generation |

---

## 🖥️ Views

1. **⚡ National Command Center** — Real-time grid overview
2. **🗣️ Agent Debate Chamber** — Watch agents analyze and argue
3. **🌐 3D Digital Twin** — Three.js national grid visualization
4. **🦢 Black Swan Simulator** — Extreme event testing
5. **🔮 Future Grid Designer** — AI infrastructure planning
6. **🔧 Self-Healing Operations** — Autonomous action audit trail
7. **💰 Economic Impact Center** — Financial analysis dashboard

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone <repo-url>
cd GRIDSENTINEL-X

# 2. Backend
cd backend
pip install -r requirements.txt
# Set your Gemini API key
export GEMINI_API_KEY=your_key_here
uvicorn main:app --reload --port 8000

# 3. Dashboard (new terminal)
cd dashboard
npm install
npm run dev

# 4. Open http://localhost:3000
```

### Docker
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
docker-compose up
```

---

## 🦢 Black Swan Scenarios

| Scenario | Type | Severity |
|----------|------|----------|
| Extreme Heat Wave — Mumbai | Climate | Critical |
| Category 4 Cyclone — Chennai | Climate | Emergency |
| Nationwide Solar Collapse | Renewable | Critical |
| Coordinated Cyber Attack — Delhi | Cyber | Emergency |
| Cascading Transformer Failure | Equipment | Emergency |
| Severe Monsoon Flooding — Mumbai | Climate | Critical |
| National Peak Demand Surge | Demand | Warning |
| Multi-Component Degradation — Bengaluru | Equipment | Warning |

Plus **custom scenario builder** — judges type any disaster in natural language.

---

## 🏙️ National Digital Twin

4-city simulated grid: **Mumbai • Delhi • Bengaluru • Chennai**

- 38 buses, 36 transmission lines, 13 substations, 12 generators
- Inter-city 220kV transmission corridors
- Real-time pandapower AC power flow simulation

---

## 📄 License

MIT — Built for hackathon demonstration purposes.
