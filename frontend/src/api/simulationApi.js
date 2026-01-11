import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const simulationApi = {
  // Get available scenarios
  getScenarios: async () => {
    const response = await axios.get(`${API_BASE_URL}/scenarios`);
    return response.data;
  },

  // Create new simulation
  createSimulation: async (scenario, spawnConfig, timeStep = 1.0) => {
    const response = await axios.post(`${API_BASE_URL}/simulation/create`, {
      scenario,
      spawn_config: spawnConfig,
      time_step: timeStep
    });
    return response.data;
  },

  // Step simulation forward
  stepSimulation: async (simulationId, steps = 1) => {
    const response = await axios.post(`${API_BASE_URL}/simulation/step`, {
      simulation_id: simulationId,
      steps
    });
    return response.data;
  },

  // Get current state
  getState: async (simulationId) => {
    const response = await axios.get(`${API_BASE_URL}/simulation/${simulationId}/state`);
    return response.data;
  },

  // Get graph structure
  getGraph: async (simulationId) => {
    const response = await axios.get(`${API_BASE_URL}/simulation/${simulationId}/graph`);
    return response.data;
  },

  // Reset simulation
  resetSimulation: async (simulationId) => {
    const response = await axios.post(`${API_BASE_URL}/simulation/${simulationId}/reset`);
    return response.data;
  },

  // Delete simulation
  deleteSimulation: async (simulationId) => {
    const response = await axios.delete(`${API_BASE_URL}/simulation/${simulationId}`);
    return response.data;
  },

  compareSimulations: async (scenario, spawnConfig, timeStep = 1.0) => {
    const response = await axios.post(`${API_BASE_URL}/simulation/compare`, {
      scenario,
      spawn_config: spawnConfig,
      time_step: timeStep
    });
    return response.data;
  },

  // PHASE 2: Execute approved intervention
  executeIntervention: async (simulationId, nodeId, action, priority = null) => {
    const response = await axios.post(
      `${API_BASE_URL}/simulation/${simulationId}/execute-intervention`,
      {
        node_id: nodeId,
        action: action,
        priority: priority
      }
    );
    return response.data;
  },

  // PHASE 4: Spawn rate control
  controlSpawnRate: async (simulationId, nodeId, rateMultiplier, duration = null) => {
    const response = await axios.post(
      `${API_BASE_URL}/simulation/${simulationId}/spawn-control`,
      {
        node_id: nodeId,
        rate_multiplier: rateMultiplier,
        duration: duration
      }
    );
    return response.data;
  },

  getSpawnControlState: async (simulationId, nodeId) => {
    const response = await axios.get(
      `${API_BASE_URL}/simulation/${simulationId}/spawn-control/${nodeId}`
    );
    return response.data;
  },

  // PHASE 4: Capacity adjustments
  adjustCapacity: async (simulationId, nodeId, adjustmentType, factor = null, duration = null) => {
    const response = await axios.post(
      `${API_BASE_URL}/simulation/${simulationId}/capacity-adjustment`,
      {
        node_id: nodeId,
        adjustment_type: adjustmentType,
        factor: factor,
        duration: duration
      }
    );
    return response.data;
  },

  getCapacityState: async (simulationId, nodeId) => {
    const response = await axios.get(
      `${API_BASE_URL}/simulation/${simulationId}/capacity/${nodeId}`
    );
    return response.data;
  },

  // PHASE 4: Advanced monitoring
  getSystemHealth: async (simulationId) => {
    const response = await axios.get(
      `${API_BASE_URL}/simulation/${simulationId}/monitoring/health`
    );
    return response.data;
  },

  getStampedePrediction: async (simulationId) => {
    const response = await axios.get(
      `${API_BASE_URL}/simulation/${simulationId}/monitoring/stampede-prediction`
    );
    return response.data;
  },

  // PHASE 4: Safety mechanisms
  getSafetyStatus: async (simulationId) => {
    const response = await axios.get(
      `${API_BASE_URL}/simulation/${simulationId}/safety/status`
    );
    return response.data;
  },

  updateSafetyConstraints: async (simulationId, constraints) => {
    const response = await axios.post(
      `${API_BASE_URL}/simulation/${simulationId}/safety/constraints`,
      constraints
    );
    return response.data;
  },

  rollbackIntervention: async (simulationId, interventionId = null) => {
    const response = await axios.post(
      `${API_BASE_URL}/simulation/${simulationId}/safety/rollback`,
      {
        intervention_id: interventionId
      }
    );
    return response.data;
  },

  // ============================================================
  // PHASE 2: New API Methods
  // ============================================================

  // Get all available scenarios with metadata
  getScenarioList: async () => {
    const response = await axios.get(`${API_BASE_URL}/scenarios/list`);
    return response.data;
  },

  // Create simulation with specific scenario
  createWithScenario: async (scenarioId, numAgents, seed = null) => {
    const response = await axios.post(`${API_BASE_URL}/simulation/create-scenario`, {
      scenario_id: scenarioId,
      num_agents: numAgents,
      seed: seed
    });
    return response.data;
  },

  // Trigger a panic event
  triggerPanic: async (simulationId, triggerType, zones, severity = 0.7) => {
    const response = await axios.post(
      `${API_BASE_URL}/simulation/${simulationId}/trigger-panic`,
      {
        trigger_type: triggerType,
        affected_zones: zones,
        severity: severity
      }
    );
    return response.data;
  },

  // Get panic state for visualization
  getPanicState: async (simulationId) => {
    const response = await axios.get(
      `${API_BASE_URL}/simulation/${simulationId}/panic-state`
    );
    return response.data;
  },

  // Case Study API
  createCaseStudy: async (config) => {
    const response = await axios.post(`${API_BASE_URL}/case-studies/create`, config);
    return response.data;
  },

  runCaseStudy: async (caseId) => {
    const response = await axios.post(`${API_BASE_URL}/case-studies/${caseId}/run`);
    return response.data;
  },

  getCaseStudyReport: async (caseId, format = 'json') => {
    const response = await axios.get(
      `${API_BASE_URL}/case-studies/${caseId}/report?format=${format}`
    );
    return response.data;
  },

  listCaseStudies: async () => {
    const response = await axios.get(`${API_BASE_URL}/case-studies`);
    return response.data;
  },

  // Blueprint Upload (Photo-to-Layout)
  uploadBlueprint: async (formData) => {
    const response = await axios.post(
      `${API_BASE_URL}/scenarios/from-blueprint`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  getBlueprintDetection: async (detectionId) => {
    const response = await axios.get(
      `${API_BASE_URL}/scenarios/from-blueprint/${detectionId}`
    );
    return response.data;
  },

  correctBlueprint: async (detectionId, correction) => {
    const response = await axios.post(
      `${API_BASE_URL}/scenarios/from-blueprint/correct`,
      { detection_id: detectionId, ...correction }
    );
    return response.data;
  },

  validateBlueprint: async (detectionId) => {
    const response = await axios.get(
      `${API_BASE_URL}/scenarios/from-blueprint/${detectionId}/validate`
    );
    return response.data;
  },

  finalizeBlueprint: async (detectionId, venueName) => {
    const response = await axios.post(
      `${API_BASE_URL}/scenarios/from-blueprint/finalize`,
      { detection_id: detectionId, venue_name: venueName }
    );
    return response.data;
  }
};
