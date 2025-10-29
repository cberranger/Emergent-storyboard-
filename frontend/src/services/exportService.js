import apiClient from './api';

export const exportService = {
  exportProject: async (projectId, format, options = {}) => {
    const response = await apiClient.get(
      `/projects/${projectId}/export/${format}`,
      { params: options }
    );
    return response.data;
  },
};
