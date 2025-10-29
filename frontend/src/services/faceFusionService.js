import apiClient from './api';

export const faceFusionService = {
  getStatus: async (params) => {
    const response = await apiClient.get('/facefusion/status', { params });
    return response.data;
  },

  enhanceFace: async (data) => {
    const response = await apiClient.post('/facefusion/enhance-face', data);
    return response.data;
  },

  adjustFaceAge: async (data) => {
    const response = await apiClient.post('/facefusion/adjust-face-age', data);
    return response.data;
  },

  swapFace: async (data) => {
    const response = await apiClient.post('/facefusion/swap-face', data);
    return response.data;
  },

  batchProcess: async (data) => {
    const response = await apiClient.post('/facefusion/batch-process', data);
    return response.data;
  },
};
