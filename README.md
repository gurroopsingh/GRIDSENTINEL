# ⚡ GRIDSENTINEL

### The World's First Autonomous Multi-Agent Energy Defense and Infrastructure Planning System

![Status](https://img.shields.io/badge/Status-Production_Ready-00ff88?style=flat-square)
![Agents](https://img.shields.io/badge/Agents-12_Active-00d4ff?style=flat-square)
![Cities](https://img.shields.io/badge/Coverage-4_Cities-8b5cf6?style=flat-square)
![AI](https://img.shields.io/badge/AI-Gemini_Powered-ff3366?style=flat-square)

---

## 🎯 What is GRIDSENTINEL?

Modern power grids are blind and reactive. They wait for catastrophic failures to happen, then respond. **GRIDSENTINEL** is an **AI-native autonomous infrastructure platform** that predicts, simulates, prevents, and self-heals power grid failures before they occur. 

This is not a traditional monitoring dashboard. This is a cognitive defense system equipped with a multi-agent AI brain, real-time digital twin physics simulation, and autonomous decision-making.

---

## 🚀 Full Feature Breakdown

### 1. 🗣️ The Multi-Agent Debate Chamber
At the core of the system is a LangGraph-orchestrated swarm of 12 specialized AI agents powered by Gemini 1.5 Pro. Instead of a single AI making blind guesses, these agents **debate** mitigation strategies in real-time, challenging each other's confidence scores before acting.
* **🎖️ Mission Commander:** Orchestrates all agents and authorizes final actions.
* **🏥 Grid Health:** Monitors voltage fluctuations and transformer temperatures.
* **🔮 Failure Prediction:** XGBoost-powered failure probability estimation.
* **🌪️ Weather Risk:** Analyzes climate impacts (e.g., cyclones, heat waves).
* **☀️ Renewable Optimizer:** Balances solar/wind intermittency with grid demand.
* **💰 Economic Intelligence:** Calculates business impact and ₹ crore losses prevented.
* **🛡️ Cybersecurity:** Detects anomalies and hunts potential SCADA threats.
* **⚡ Grid Optimizer:** Optimizes load distribution across substations.
* **🔧 Self-Healing:** Generates autonomous physical repair actions (e.g., line switching).
* **🚨 Emergency Response:** Activates crisis management protocols for hospitals.
* **🔬 Energy Scientist:** Discovers long-term patterns and generates infrastructure hypotheses.

### 2. 🌐 4-City National Digital Twin
We built a highly realistic simulated national grid mapping **Mumbai, Delhi, Bengaluru, and Chennai**.
* **Physics Engine:** Runs live AC/DC power flow calculations using Pandapower.
* **Scale:** Simulates 42 buses, 33 transmission lines, 13 substations, and 12 major generators (Thermal, Nuclear, Solar, Wind).
* **Visuals:** Rendered in a fully interactive 3D environment using Three.js.

### 3. 🦢 Black Swan Disaster Simulator
Judges can inject extreme, low-probability disaster events to watch the AI autonomously defend the grid. Built-in scenarios include:
* Extreme Heat Wave — Mumbai
* Category 4 Cyclone — Chennai
* Nationwide Solar Collapse
* Coordinated Cyber Attack — Delhi
* Cascading Transformer Failure

### 4. 🔧 Autonomous Self-Healing
When a failure occurs (N-1 contingency), the system doesn't just alert a human. It autonomously executes operations to prevent a cascading collapse:
* Generator Redispatching
* Transmission Line Switching
* Dynamic Load Shedding (saving critical infrastructure like hospitals first)

### 5. 🔮 Future Grid Designer
An AI infrastructure planning tool. Prompt the AI with commands like *"Redesign Mumbai's grid for 100% renewables by 2035,"* and it will generate multi-crore infrastructure blueprints, calculating ROI and stability improvements.

### 6. 💰 Economic Impact Center
Every blackout carries a financial cost. The platform actively calculates the economic damage of a potential failure versus the cost of the AI's preventative measures, demonstrating exactly how many ₹ Crores were saved.

---

## 🏗️ Architecture

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js, Three.js, Tailwind, Framer Motion | High-performance, animated Mission Control UI |
| **Backend** | FastAPI, WebSockets | Low-latency real-time API & telemetry streaming |
| **AI Brain** | LangGraph, Gemini 1.5 Pro | 12 autonomous debating agents |
| **Simulation** | Pandapower | AC/DC physics power flow & cascading failure engine |
| **Database** | SQLite / SQLAlchemy | Persistent agent memory and telemetry storage |

---

## 💻 How to Run Locally

To run the full stack, you need two terminal windows:

### Terminal 1: Start the AI Backend
```powershell
cd GRIDSENTINEL/backend
python -m venv venv
.\venv\Scripts\activate

# Install AI and Physics Simulation dependencies
pip install -r requirements.txt

# Create a .env file and add your Gemini API Key
echo "GEMINI_API_KEY=your_key_here" > .env

# Initialize DB and start the server
python -c "import asyncio; from db.connection import init_db; asyncio.run(init_db())"
uvicorn main:app --reload --port 8000
```

### Terminal 2: Start the Dashboard Frontend
```powershell
cd GRIDSENTINEL/dashboard
npm install
npm run dev
```

Finally, open your browser and navigate to: **[http://localhost:3000](http://localhost:3000)**

---

## 📄 License
MIT License.
