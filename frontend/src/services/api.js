import axios from 'axios';
import { toast } from 'sonner';
import { API } from '@/config';

const apiClient = axios.create({
  baseURL: API,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    
    if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout - operation took too long');
    } else if (error.response?.status === 404) {
      toast.error('Resource not found');
    } else if (error.response?.status === 500) {
      toast.error('Server error occurred');
    } else if (!error.config?.skipErrorToast) {
      toast.error(errorMessage);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
