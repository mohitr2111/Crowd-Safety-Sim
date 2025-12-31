# AI‑Powered Crowd Safety Platform
Predictive AI for stampede prevention + real‑time crowd flow interventions

## Why this exists (Problem)
Large venues (stadiums, railway stations, festivals) often react *after* dangerous crowding happens. Our platform simulates crowds using a digital‑twin venue graph and applies an RL policy to recommend/execute interventions (reroute, reduce inflow, temporary closures) before a stampede forms.

## What we built (Round 1)
### 1) Digital Twin + Multi‑Agent Simulation (Backend)
- Venue modeled as a **graph**: nodes = zones/exits/corridors, edges = paths with capacity/width.
- Crowd modeled as **agents** that navigate via shortest paths and slow down under high density.
- Real‑time metrics: max density, agents evacuated, danger zones, violations.

### 2) AI Intervention Layer (Q‑Learning)
We trained a Q‑Learning policy that chooses actions based on discretized crowd state:
- Actions: `no_action`, `reduce_inflow_25`, `reduce_inflow_50`, `close_inflow`, `reroute_to_alt_exit`
- Goal: reduce max density + reduce danger zones/violations + reduce evacuation time.

### 3) Frontend Dashboard (React)
- Live heatmap visualization (node density color map)
- Scenario builder UI (design zones, connect edges, mark exits)
- “AI vs Baseline” comparison dashboard with charts + action timeline

---

## System Architecture (High level)
Frontend (React + Tailwind)
  ↕ REST API
Backend (FastAPI + Python)
  ├─ Simulation Engine (multi-agent loop)
  ├─ Digital Twin (graph topology + density stats)
  ├─ RL Agent (Q-learning policy)
  └─ Comparison Runner (baseline vs optimized)

---

## Flow Charts / DFDs (mandatory)

### A) DFD: Live Simulation (Level 1)
User (UI)
  → POST /simulation/create (scenario + spawn config)
Backend (FastAPI)
  → creates Simulator(session_id)
  → returns initial state
User (UI)
  → POST /simulation/step (session_id, steps)
Backend
  → sim.step() updates agents, densities, stats
  → returns updated state
UI
  → renders heatmap + agents + alerts

### B) DFD: AI vs Baseline Comparison
User (UI)
  → POST /simulation/compare (scenario + spawn config)
Backend
  → load RL model
  → run_baseline()
  → run_optimized() (apply actions while stepping)
  → return comparison report (metrics + action samples)

### C) RL Decision Loop (Policy Control)
For each simulation step:
  1) read node densities
  2) discretize state (density bucket + occupancy bucket)
  3) choose action (policy exploitation)
  4) apply intervention (wait time / reroute / inflow control)
  5) step simulation

(See /docs/flows.md for expanded flow diagrams.)

---

## Key Results (Round 1 – Verified)
### Stadium Exit Stress Test (1100 agents)
**Baseline (No AI)**
- Max density: 5.00 p/m²
- Danger violations: 7
- Evacuation time: 59s
- Agents reached goal: 1100

**RL‑Optimized**
- Max density: 4.575 p/m²
- Danger violations: 5
- Evacuation time: 55s
- Agents reached goal: 1100

**Improvement**
- Density reduction: 8.5%
- Violations prevented: 2
- Time saved: 4s

Sample AI actions:
- t=2s `reroute_to_alt_exit` @ corridor_north (density 3.125)
- t=6s `reduce_inflow_50` @ corridor_north (density 4.575)

---

## What makes this original / out‑of‑the‑box (Judging criteria)
- **Digital twin + RL policy control**: Instead of only showing density heatmaps, we add a policy that *acts* on the system and can be compared vs baseline.
- **Human‑interpretable interventions**: Actions are explainable (“reduce inflow 25%”, “reroute to alt exits”) and logged with timestamps, so operators can trust it.
- **Scenario builder approach**: Instead of hardcoding one stadium, the UI supports building venue graphs and testing interventions.

---

## How to run locally
### Backend
cd backend
python -m venv venv
venv\Scripts\activate # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000


### Frontend
cd frontend
npm install
npm run dev



Open: http://localhost:5173 

---

## API Endpoints (Core)
- GET `/scenarios`
- POST `/simulation/create`
- POST `/simulation/step`
- GET `/simulation/{id}/state`
- GET `/simulation/{id}/graph`
- GET `/simulation/{id}/stadium-status`
- POST `/simulation/compare`

---

## Round 2 – Improvements Planned (mandatory)
> (Leave placeholders here if you want to fill later)

### ✅ Round 2 Goals
    Photo/Blueprint → Auto Venue Graph (“Photo‑to‑Layout”)
**Goal:** Upload a venue blueprint/photo and auto-generate the digital twin (zones/exits/paths).

**What will be added**
- Blueprint upload + interactive annotation (correct exit/zone detection)
- Auto-generate `scenario.json` (nodes/edges, area estimates, capacities)
- Validate topology automatically (no disconnected exits)

**Tech needed**
- **Backend:** Python, OpenCV, YOLOv8 (Ultralytics), NumPy
- **Optional OCR:** Tesseract (to read measurements/labels)
- **Frontend:** React canvas annotation (Konva.js / Fabric.js) + drag handles
- **Storage:** S3/Cloud storage for uploaded images
- **Output format:** JSON scenario compatible with simulator [file:46]

---

### B) Better Panic Propagation for Triggers (Crowd Surge + Speed Changes)
**Goal:** Make triggers (fire, bomb threat, gate malfunction) realistically change behavior.

**What will be added**
- “Panic state” for agents (speed multiplier + reduced patience)
- “Surge” modeling: sudden inflow spikes into bottlenecks
- Trigger-specific effects:
  - Fire → avoid zone + reroute around blocked areas
  - Bomb threat → rapid exit rush + density spike near exits
  - Gate malfunction → reduced capacity / blocked inflow for that gate

**Tech needed**
- **Backend simulation:** new trigger module + per-agent panic variables
- **Data model:** trigger schema + severity + affected zone
- **Evaluation:** replayable trigger test packs

**Why it improves the model**
- RL will learn *different* optimal actions for different emergencies because the environment dynamics change.
---

### D) Better RL Training (more scenarios, multi‑seed evaluation, stable learning)
**Goal:** Make the RL policy robust, consistent, and judge-proof.

**What will be added**
- Multi-scenario training: stadium + railway + festival layouts
- Multi-seed evaluation:
  - run each scenario 50–100 times with different random seeds
  - report mean ± std (not just one run)
- Reward stabilization:
  - tune reward weights to reduce oscillations
  - penalize deadlocks and unnecessary closures

**Tech needed**
- **Python:** NumPy/Pandas for evaluation summaries
- **Experiment tracking:** MLflow or simple JSON logs
- **CI:** automated benchmark tests before merge

### F) RL Model Working Real Case Studies (mandatory-impact feature)
**Goal:** Prove usefulness via realistic case-study packs.

**What will be added**
- “Case Study Mode” page:
  - scenario summary
  - baseline vs AI metrics
  - timeline of interventions
  - downloadable report JSON
- At least 3 reproducible case studies:
  - Stadium exit bottleneck
  - Railway platform rush
  - Pilgrimage-style corridor + gate malfunction

**Tech needed**
- JSON case-pack format (scenario + spawn + trigger + expected outputs)
- Frontend storytelling view (timeline + charts)
- Backend report export endpoint (downloadable artifact)

## Round 2: Trigger‑Aware Optimization (Model will get better at all triggers)
In Round 2, the RL model will be trained and evaluated on **triggered environments** (fire, bomb threat, gate malfunction, medical emergency), where triggers modify:
- path availability (blocked edges)
- movement speed (panic)
- inflow spikes (surge)
- exit capacities (partial closures)

This makes the learned policy **trigger-aware**, improving decisions beyond pure density thresholds. [file:53]

---
---

## Case Study (1 example – for judges)
### “Mahakumbh‑like” scenario replay (What‑If simulation)
We model a high‑pressure crowd movement scenario with:
- Converging flows into a narrow corridor (bottleneck)
- A trigger event (gate malfunction / perceived threat)
- Panic behavior: increased inflow toward a single exit

**Baseline outcome (no interventions):**
- Density spikes beyond safe threshold at the bottleneck → repeated danger violations.

**With AI interventions enabled:**
- Early rerouting to alternative exits
- Inflow throttling at corridor entry
- Temporary closure when density becomes critical

**Result:**
The RL policy reduces peak density and prevents violations by distributing load across multiple exits and delaying inflow before the bottleneck becomes irreversible.

(For Round 2, we will attach a full reproducible “Mahakumbh case pack”: scenario JSON + run logs + comparison report + dashboard screenshots.)

---

## Project Structure (important folders)
backend/
  main.py            # FastAPI API
  simulation/        # simulator, digital twin, agents, scenarios
  rl/                # q-learning agent, training, comparison runner
  ai/                # Not Fully Implemented
frontend/
  src/components/    # canvas view, scenario builder, dashboards
docs/
  flows.md           # technical flows/DFDs
  Rl_training_history

---
