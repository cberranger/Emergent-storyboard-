import apiClient from './api';

export const styleTemplateService = {
  getTemplates: async () => {
    const response = await apiClient.get('/style-templates');
    return response.data;
  },

  getTemplate: async (templateId) => {
    const response = await apiClient.get(`/style-templates/${templateId}`);
    return response.data;
  },

  createTemplate: async (templateData) => {
    const response = await apiClient.post('/style-templates', templateData);
    return response.data;
  },

  updateTemplate: async (templateId, templateData) => {
    const response = await apiClient.put(`/style-templates/${templateId}`, templateData);
    return response.data;
  },

  deleteTemplate: async (templateId) => {
    const response = await apiClient.delete(`/style-templates/${templateId}`);
    return response.data;
  },

  useTemplate: async (templateId) => {
    const response = await apiClient.post(`/style-templates/${templateId}/use`);
    return response.data;
  },
};
