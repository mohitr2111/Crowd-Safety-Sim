### ✅ Round 2 Goals


### A) Photo/Blueprint → Auto Venue Graph (“Photo‑to‑Layout”)
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
- **Output format:** JSON scenario compatible with simulator

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

### C) Better RL Training (more scenarios, multi‑seed evaluation, stable learning)
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

### D) RL Model Working Real Case Studies (mandatory-impact feature)
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

### E: Trigger‑Aware Optimization (Model will get better at all triggers)
In Round 2, the RL model will be trained and evaluated on **triggered environments** (fire, bomb threat, gate malfunction, medical emergency), where triggers modify:
- path availability (blocked edges)
- movement speed (panic)
- inflow spikes (surge)
- exit capacities (partial closures)

This makes the learned policy **trigger-aware**, improving decisions beyond pure density thresholds. 

---