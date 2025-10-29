import apiClient from './api';

export const generationService = {
  generate: async (generationData) => {
    const response = await apiClient.post('/generate', generationData);
    return response.data;
  },

  generateV1: async (generationData) => {
    const response = await apiClient.post('/v1/generate', generationData);
    return response.data;
  },

  generateBatch: async (batchData) => {
    const response = await apiClient.post('/generate/batch', batchData);
    return response.data;
  },
};
