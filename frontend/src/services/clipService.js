import apiClient from './api';

export const clipService = {
  createClip: async (clipData) => {
    const response = await apiClient.post('/clips', clipData);
    return response.data;
  },

  getClip: async (clipId) => {
    const response = await apiClient.get(`/clips/${clipId}`);
    return response.data;
  },

  updateClip: async (clipId, clipData) => {
    const response = await apiClient.put(`/clips/${clipId}`, clipData);
    return response.data;
  },

  deleteClip: async (clipId) => {
    const response = await apiClient.delete(`/clips/${clipId}`);
    return response.data;
  },

  updateClipTimelinePosition: async (clipId, positionData) => {
    const response = await apiClient.put(`/clips/${clipId}/timeline-position`, positionData);
    return response.data;
  },

  updateClipPrompts: async (clipId, params) => {
    const response = await apiClient.put(`/clips/${clipId}/prompts`, null, { params });
    return response.data;
  },

  selectClipContent: async (clipId, params) => {
    const response = await apiClient.put(`/clips/${clipId}/select-content`, null, { params });
    return response.data;
  },

  getClipGallery: async (clipId) => {
    const response = await apiClient.get(`/clips/${clipId}/gallery`);
    return response.data;
  },

  createClipAlternate: async (clipId) => {
    const response = await apiClient.post(`/clips/${clipId}/create-alternate`);
    return response.data;
  },
};
