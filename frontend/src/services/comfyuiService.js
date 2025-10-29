import apiClient from './api';

export const comfyuiService = {
  getServers: async () => {
    const response = await apiClient.get('/comfyui/servers');
    return response.data;
  },

  getServer: async (serverId) => {
    const response = await apiClient.get(`/comfyui/servers/${serverId}`);
    return response.data;
  },

  createServer: async (serverData) => {
    const response = await apiClient.post('/comfyui/servers', serverData);
    return response.data;
  },

  deleteServer: async (serverId) => {
    const response = await apiClient.delete(`/comfyui/servers/${serverId}`);
    return response.data;
  },

  getServerInfo: async (serverId) => {
    const response = await apiClient.get(`/comfyui/servers/${serverId}/info`);
    return response.data;
  },

  getServerWorkflows: async (serverId) => {
    const response = await apiClient.get(`/comfyui/servers/${serverId}/workflows`);
    return response.data;
  },
};
