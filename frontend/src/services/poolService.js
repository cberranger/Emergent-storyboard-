import apiClient from './api';

export const poolService = {
  getPoolItems: async (projectId) => {
    const response = await apiClient.get(`/pool/${projectId}`);
    return response.data;
  },

  addToPool: async (poolData) => {
    const response = await apiClient.post('/pool', poolData);
    return response.data;
  },

  deletePoolItem: async (itemId) => {
    const response = await apiClient.delete(`/pool/item/${itemId}`);
    return response.data;
  },
};
