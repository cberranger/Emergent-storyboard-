import apiClient from './api';

export const modelService = {
  getModels: async (params) => {
    const response = await apiClient.get('/models', { params });
    return response.data;
  },

  getModelPresets: async (modelName) => {
    const response = await apiClient.get(`/models/presets/${encodeURIComponent(modelName)}`);
    return response.data;
  },

  getModelParameters: async (modelName) => {
    const response = await apiClient.get(`/models/parameters/${encodeURIComponent(modelName)}`);
    return response.data;
  },

  syncModelToCivitai: async (modelId) => {
    const response = await apiClient.post(`/models/${modelId}/sync-civitai`);
    return response.data;
  },

  searchCivitai: async (modelId, searchData) => {
    const response = await apiClient.post(`/models/${modelId}/search-civitai`, searchData);
    return response.data;
  },

  linkToCivitai: async (modelId, linkData) => {
    const response = await apiClient.post(`/models/${modelId}/link-civitai`, linkData);
    return response.data;
  },

  syncServerModels: async (serverId) => {
    const response = await apiClient.post(`/servers/${serverId}/sync-models`);
    return response.data;
  },
};
