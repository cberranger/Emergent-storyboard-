import apiClient from './api';

export const characterService = {
  getCharacters: async (params) => {
    const response = await apiClient.get('/characters', { params });
    return response.data;
  },

  getCharacter: async (characterId) => {
    const response = await apiClient.get(`/characters/${characterId}`);
    return response.data;
  },

  createCharacter: async (characterData) => {
    const response = await apiClient.post('/characters', characterData);
    return response.data;
  },

  updateCharacter: async (characterId, characterData) => {
    const response = await apiClient.put(`/characters/${characterId}`, characterData);
    return response.data;
  },

  deleteCharacter: async (characterId) => {
    const response = await apiClient.delete(`/characters/${characterId}`);
    return response.data;
  },

  generateCharacter: async (characterId, generationData) => {
    const response = await apiClient.post(`/characters/${characterId}/generate`, generationData);
    return response.data;
  },

  uploadFaceImage: async (formData) => {
    const response = await apiClient.post('/upload-face-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadCharacterImages: async (formData) => {
    const response = await apiClient.post('/upload-character-images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  generateCharacterProfiles: async (data) => {
    const response = await apiClient.post('/generate-character-profiles', data);
    return response.data;
  },
};
