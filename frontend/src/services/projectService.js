import apiClient from './api';

export const projectService = {
  getProjects: async () => {
    const response = await apiClient.get('/projects');
    return response.data;
  },

  getProject: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}`);
    return response.data;
  },

  createProject: async (projectData) => {
    const response = await apiClient.post('/projects', projectData);
    return response.data;
  },

  updateProject: async (projectId, projectData) => {
    const response = await apiClient.put(`/projects/${projectId}`, projectData);
    return response.data;
  },

  deleteProject: async (projectId) => {
    const response = await apiClient.delete(`/projects/${projectId}`);
    return response.data;
  },

  getProjectScenes: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}/scenes`);
    return response.data;
  },

  getProjectClips: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}/clips`);
    return response.data;
  },

  getProjectTimeline: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}/timeline`);
    return response.data;
  },

  uploadProjectMusic: async (projectId, formData) => {
    const response = await apiClient.post(`/projects/${projectId}/upload-music`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
