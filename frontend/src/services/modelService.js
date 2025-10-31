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

  getModelConfigurations: async (modelId) => {
    const response = await apiClient.get(`/api/v1/models/${modelId}/configurations`);
    return response.data;
  },

  getBaseModelConfigurations: async (baseModelType) => {
    const response = await apiClient.get(`/api/v1/models/configurations/base/${baseModelType}`);
    return response.data;
  },

  getConfiguration: async (configId) => {
    const response = await apiClient.get(`/api/v1/models/configurations/${configId}`);
    return response.data;
  },

  createModelConfiguration: async (modelId, configData) => {
    const response = await apiClient.post(`/api/v1/models/${modelId}/configurations`, configData);
    return response.data;
  },

  createBaseModelConfiguration: async (baseModelType, configData) => {
    const response = await apiClient.post(`/api/v1/models/configurations/base/${baseModelType}`, configData);
    return response.data;
  },

  updateConfiguration: async (configId, updateData) => {
    const response = await apiClient.put(`/api/v1/models/configurations/${configId}`, updateData);
    return response.data;
  },

  deleteConfiguration: async (configId) => {
    const response = await apiClient.delete(`/api/v1/models/configurations/${configId}`);
    return response.data;
  },

  getDefaultConfiguration: async (modelId) => {
    const response = await apiClient.get(`/api/v1/models/${modelId}/configurations/default`);
    return response.data;
  },
};
