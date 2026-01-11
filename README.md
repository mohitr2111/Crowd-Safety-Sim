
![Visual Overview](Docs/Website_Name.png)

# Introduction
Crowd-Safety-Sim is an AI-powered crowd management and safety simulation platform designed for large venues, public events, and urban environments where managing crowd density is critical to preventing accidents and emergencies.

The platform enables users to create realistic digital twins of physical spaces and simulate crowd movement using intelligent agents that respond dynamically to congestion, pathways, and exit capacities. By combining real-time simulation with predictive analytics, Crowd-Safety-Sim allows planners and authorities to visualize crowd behavior, identify high-risk zones, and evaluate safety strategies before deploying them in the real world.

To move beyond passive monitoring, Crowd-Safety-Sim integrates an AI-driven intervention layer based on reinforcement learning. This system actively learns optimal strategies—such as controlling inflow, rerouting movement, or managing exits—to reduce unsafe densities and improve evacuation outcomes. All simulations and interventions are tracked transparently, enabling clear comparison between baseline scenarios and AI-assisted decision making.

Crowd-Safety-Sim provides a comprehensive platform for designing, simulating, and optimizing crowd safety using interactive dashboards, visual heatmaps, and intelligent automation—helping decision-makers ensure safer, more resilient public spaces with confidence.

## Why this exists (Problem)
Large venues (stadiums, railway stations, festivals) often react *after* dangerous crowding happens. Our platform simulates crowds using a digital‑twin venue graph and applies an RL policy to recommend/execute interventions (reroute, reduce inflow, temporary closures) before a stampede forms.

## Tech Stack
  Core Framework & Language

  Python – Primary language for simulation, AI logic, and backend services

  FastAPI – High-performance backend framework for building REST APIs

  JavaScript / TypeScript – Frontend logic and type-safe development

  Simulation & Modeling

  Custom Crowd Simulation Engine – Agent-based crowd movement modeling

  Graph-Based Venue Modeling – Digital twin representation of real-world spaces

  Shortest Path Algorithms – Navigation logic for crowd agents

  Density & Flow Metrics – Real-time calculation of congestion and safety thresholds

  AI & Machine Learning

  Reinforcement Learning (Q-Learning) – AI-driven intervention strategy learning

  NumPy – Numerical computations for simulation and learning

  Custom Reward Functions – Optimized for crowd safety and evacuation efficiency

  Backend & API

  FastAPI REST Services – Simulation control, AI actions, and data exchange

  JSON-based APIs – Lightweight communication between frontend and backend

  Python Modular Architecture – Separation of simulation, AI, and API layers

  Frontend & Visualization

  React – Interactive user interface

  Tailwind CSS – Utility-first styling for rapid UI development

  Heatmap Visualizations – Real-time crowd density representation

  Scenario Builder UI – Configure venues, crowd size, and inflow parameters

  Data Handling

  JSON Configuration Files – Venue layouts, simulation parameters, and results

  In-Memory State Management – Fast simulation iteration and comparison

  System Architecture

  Baseline vs AI-Controlled Comparison – Performance benchmarking

  Modular Design – Easily extensible for advanced RL models or real-world sensor data

  Digital Twin Architecture – Mirrors physical crowd environments for safe testing

  Development & Tooling

  Git & GitHub – Version control and collaboration

  VS Code – Primary development environment

  Python Virtual Environments – Dependency isolation

  Built to simulate, predict, and prevent crowd safety risks using AI-powered digital twins and intelligent interventions.


## Crowd Safety Simulation System - Visual Overview

![Visual Overview](Docs/Visual_Overview.png)

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

## Inputs & Outputs
Inputs

Venue Layout (Digital Twin) – Zones, paths, exits, and capacities

Crowd Parameters – Crowd size, inflow rate, entry points

Simulation Settings – Time steps, duration, safety thresholds

AI Configuration – State space, action space, reward parameters

Outputs

Crowd Density Metrics – Density per zone over time

Evacuation Statistics – Total evacuation time and flow rates

Safety Indicators – Congestion and threshold violations

AI Decisions – Selected interventions and performance metrics

Visualization Data – Heatmaps and comparison results


## Execution Model

At runtime:

Simulation and AI configurations are validated

The crowd simulation is executed step-by-step

The AI intervention layer evaluates the current state

Decisions are applied to the simulation

Outputs are generated and exposed to the frontend

## Core Principles

Safety First – Minimize unsafe crowd density and congestion

Predictive Intervention – Act before critical thresholds are breached

Digital Twin Accuracy – Realistic modeling of physical venues

AI-Driven Decisions – Reinforcement learning–based optimization

Transparency – Clear comparison between baseline and AI-controlled runs


## Git-Based Collaboration

This project follows a standard Git-based collaboration workflow to ensure safe development, clear reviews, and stable versioning.



## Workflow Overview
Step  	Action	                Description
 1	  Fork Repository	        Contributors fork the main repository to create an isolated workspace.
 2	  Create Feature Branch	  Changes are made on a separate branch inside the fork.
 3	  Develop & Commit      	Features, fixes, or experiments are implemented and committed incrementally.
 4  	Push Changes	          Commits are pushed to the contributor’s forked repository.
 5	  Open Pull Request	      A pull request is created to propose changes to the main branch.
 6	  Review Process	        Maintainers review code, suggest changes, or request improvements.
 7	  Approval / Rejection	  Pull request is approved or rejected based on review feedback.
 8	  Merge	                  Approved changes are merged into the main branch.
 9	  Version Update	        A new version or update is created after successful merge.

![Git-Based Collaboration](Docs/Git_Based_Collaboration.png)



## Execution Sequence
![Git-Based Collaboration](Docs/Execution_Sequence.png)



## Key Responsibilities of the Execution Engine

1) Configuration & Validation

Validate simulation and AI input configurations

Ensure safety thresholds and parameters are correctly defined

2) Simulation Control

Initialize the digital twin and crowd environment

Execute the crowd simulation step-by-step

3) AI Integration

Invoke the AI intervention layer at each timestep

Apply AI-driven actions to control crowd flow and density

4) Metrics & Monitoring

Track crowd density, flow rates, and safety violations

Update system state in real time

5) Output & Integration

Generate structured outputs for analysis and visualization

Expose simulation results through backend APIs to the frontend




## What Problem This Solves
Risk	                               Mitigation
Crowd congestion hotspots	        Real-time density tracking and heatmaps
Late reaction to crowd buildup	  Predictive AI-based intervention
Unsafe evacuation planning	      Simulation-based evacuation analysis
Manual crowd control decisions	  Reinforcement learning–driven actions
Unverifiable safety improvements	Baseline vs AI-controlled comparison


## What Gets Recorded During Simulation
Event	                                 Purpose
Scenario initialization	        Defines venue and crowd parameters
Simulation step execution     	Tracks crowd movement over time
Density threshold breach	      Identifies unsafe congestion
AI intervention action	        Records applied control decisions
Evacuation completion	          Measures overall safety performance
Result generation	              Enables analysis and visualization

## Core Concepts
Concept                           	Description
Digital Twin	            Virtual representation of a real venue
Agent-Based Modeling	    Individual crowd agents with movement logic
Density Metrics	          Crowd concentration per zone
Reinforcement Learning	  AI-driven decision making
Intervention Actions	    Flow control and rerouting strategies
Scenario Comparison	      Baseline vs AI-assisted evaluation


## State-Based Decision Model
Only state summaries are passed to the AI layer.

State Element	        Represents
Zone density	      Current crowd load per area
Flow rate	          Movement speed between zones
Exit pressure	      Congestion near exits
Time step	          Simulation progression
Safety score	      Overall risk indicator

Any deviation from safe thresholds triggers AI evaluation and response.

## Simulation Execution Flow

Scenario configuration is loaded

Digital twin environment is initialized

Crowd agents are spawned

Simulation advances step-by-step

AI evaluates current crowd state

Intervention actions are applied

Metrics and outputs are recorded

## User Authorization Model
Action	                    Authorization
Create scenario 	        Authorized user
Run simulation	          System-controlled
Enable AI intervention  	Config-level permission
View results	            Read-only access
Modify parameters	        Editor-level access

All simulation runs are traceable to configuration inputs.

## Execution Engine Responsibilities
Responsibility                	Description
Configuration validation	   Ensures safe and valid parameters
Simulation control	         Manages time steps and agents
AI invocation	Calls          RL model at runtime
State updates  	             Maintains real-time metrics
Output generation	           Produces visualization-ready data


## Safety & Reliability Guarantees
Guarantee	            Achieved By
Predictive safety	  AI-based early intervention
Risk reduction	    Density-aware control
Transparency	      Measurable simulation metrics
Repeatability	      Deterministic simulation setup
Cost efficiency	    Virtual testing instead of live trials





## Case Study (1 example – for judges)

“Mahakumbh‑like” scenario replay (What‑If simulation)
We model a high‑pressure crowd movement scenario with:

    Converging flows into a narrow corridor (bottleneck)
    A trigger event (gate malfunction / perceived threat)
    Panic behavior: increased inflow toward a single exit

Baseline outcome (no interventions):
  Density spikes beyond safe threshold at the bottleneck → repeated danger violations.

With AI interventions enabled:
    Early rerouting to alternative exits
    Inflow throttling at corridor entry
    Temporary closure when density becomes critical

Result: The RL policy reduces peak density and prevents violations by distributing load across multiple exits and delaying inflow before the bottleneck becomes irreversible.

## Visual Evidence (Simulation & Results)

> The following visuals are generated directly from the running system
> and are included in `/docs` for reproducibility.

![Density Heatmap](Docs/Heat_Map.png)
![Baseline vs AI Density Over Time](Docs/Model_Test.png)
![Baseline vs AI Density Over Time](Docs/Model_Test(2).png)
![AI Action Timeline](Docs/AI_recommendations.png)
