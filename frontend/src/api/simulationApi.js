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
  }
};
