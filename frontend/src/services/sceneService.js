import apiClient from './api';

export const sceneService = {
  createScene: async (sceneData) => {
    const response = await apiClient.post('/scenes', sceneData);
    return response.data;
  },

  getScene: async (sceneId) => {
    const response = await apiClient.get(`/scenes/${sceneId}`);
    return response.data;
  },

  updateScene: async (sceneId, sceneData) => {
    const response = await apiClient.put(`/scenes/${sceneId}`, sceneData);
    return response.data;
  },

  deleteScene: async (sceneId) => {
    const response = await apiClient.delete(`/scenes/${sceneId}`);
    return response.data;
  },

  getSceneClips: async (sceneId) => {
    const response = await apiClient.get(`/scenes/${sceneId}/clips`);
    return response.data;
  },

  getSceneTimelineAnalysis: async (sceneId) => {
    const response = await apiClient.get(`/scenes/${sceneId}/timeline-analysis`);
    return response.data;
  },

  createSceneAlternate: async (sceneId) => {
    const response = await apiClient.post(`/scenes/${sceneId}/create-alternate`);
    return response.data;
  },
};
