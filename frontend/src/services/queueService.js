import apiClient from './api';

export const queueService = {
  getJobs: async (params) => {
    const response = await apiClient.get('/queue/jobs', { params });
    return response.data;
  },

  retryJob: async (jobId) => {
    const response = await apiClient.post(`/queue/jobs/${jobId}/retry`);
    return response.data;
  },

  cancelJob: async (jobId) => {
    const response = await apiClient.post(`/queue/jobs/${jobId}/cancel`);
    return response.data;
  },

  deleteJob: async (jobId) => {
    const response = await apiClient.delete(`/queue/jobs/${jobId}`);
    return response.data;
  },

  clearQueue: async (params) => {
    const response = await apiClient.delete('/queue/clear', { params });
    return response.data;
  },
};
