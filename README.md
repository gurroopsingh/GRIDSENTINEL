# ⚡ GRIDSENTINEL

### The World's First Autonomous Multi-Agent Energy Defense and Infrastructure Planning System

![Status](https://img.shields.io/badge/Status-Production_Ready-00ff88?style=flat-square)
![Agents](https://img.shields.io/badge/Agents-12_Active-00d4ff?style=flat-square)
![Cities](https://img.shields.io/badge/Coverage-4_Cities-8b5cf6?style=flat-square)
![AI](https://img.shields.io/badge/AI-Gemini_Powered-ff3366?style=flat-square)

---

## 🎯 What is GRIDSENTINEL?

Modern power grids are blind and reactive. They wait for catastrophic failures to happen, then respond. **GRIDSENTINEL** is an **AI-native autonomous infrastructure platform** that predicts, simulates, prevents, and self-heals power grid failures before they occur. 

Built for the **FAR AWAY 2026 Finals**, this is not a monitoring dashboard. This is a cognitive defense system equipped with a multi-agent AI brain, real-time digital twin simulation, and autonomous decision-making.

---

## 🚀 Key Innovations

1. **⚡ National Command Center:** Real-time grid overview with beautiful NASA-style dark mode UI.
2. **🗣️ Agent Debate Chamber:** Watch 12 specialized LangGraph AI agents (Commander, Economist, Energy Scientist) analyze telemetry and argue over the best mitigation strategies in real-time.
3. **🌐 3D Digital Twin:** Interactive physics simulation (Pandapower + Three.js) spanning Mumbai, Delhi, Bengaluru, and Chennai.
4. **🦢 Black Swan Simulator:** Inject extreme disaster events (Category 5 Cyclones, Cyber Attacks, Solar Collapses) and watch the AI autonomously self-heal the grid.
5. **🔮 Future Grid Designer:** AI infrastructure planning tool that generates multi-crore grid upgrades for 2035.

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

## 🦢 Built-In "Black Swan" Scenarios

Trigger these directly from the dashboard to watch the agents spring into action:

| Scenario | Type | Severity |
|----------|------|----------|
| Extreme Heat Wave — Mumbai | Climate | Critical |
| Category 4 Cyclone — Chennai | Climate | Emergency |
| Nationwide Solar Collapse | Renewable | Critical |
| Coordinated Cyber Attack — Delhi | Cyber | Emergency |
| Cascading Transformer Failure | Equipment | Emergency |

*Plus a Custom Scenario Builder where judges can type any disaster in natural language.*

---

## 📄 License
MIT License. Built for presentation purposes at the FAR AWAY 2026 Finals.
