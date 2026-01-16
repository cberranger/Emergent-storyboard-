import axios from 'axios';
import { config } from '../config';

const BASE_URL = config.apiUrl;

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor for transforming outgoing requests
 */
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for transforming responses and handling errors
 */
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  async (error) => {
    const originalRequest = error.config;

    if (!error.response) {
      console.error('Network error:', error.message);
      return Promise.reject({
        message: 'Network error. Please check your connection.',
        type: 'NETWORK_ERROR',
      });
    }

    if (error.response.status >= 500 && !originalRequest._retry) {
      originalRequest._retry = true;
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

      if (originalRequest._retryCount <= 2) {
        const delay = originalRequest._retryCount * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
        return apiClient(originalRequest);
      }
    }

    const errorResponse = {
      message: error.response?.data?.detail || error.response?.data?.message || error.message,
      status: error.response?.status,
      type: 'API_ERROR',
      data: error.response?.data,
    };

    return Promise.reject(errorResponse);
  }
);

/**
 * Helper function for retryable requests
 * @param {Function} requestFn - The request function to retry
 * @param {number} maxRetries - Maximum number of retry attempts
 * @param {number} delayMs - Delay between retries in milliseconds
 * @returns {Promise} The result of the request
 */
export const withRetry = async (requestFn, maxRetries = 3, delayMs = 1000) => {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries - 1) {
        await new Promise((resolve) => setTimeout(resolve, delayMs * (attempt + 1)));
      }
    }
  }

  throw lastError;
};

/**
 * Request/Response transformers
 */
export const transformers = {
  /**
   * Transform camelCase to snake_case for backend
   * @param {Object} obj - Object to transform
   * @returns {Object} Transformed object
   */
  toSnakeCase: (obj) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(transformers.toSnakeCase);

    return Object.keys(obj).reduce((acc, key) => {
      const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
      acc[snakeKey] = transformers.toSnakeCase(obj[key]);
      return acc;
    }, {});
  },

  /**
   * Transform snake_case to camelCase for frontend
   * @param {Object} obj - Object to transform
   * @returns {Object} Transformed object
   */
  toCamelCase: (obj) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(transformers.toCamelCase);

    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      acc[camelKey] = transformers.toCamelCase(obj[key]);
      return acc;
    }, {});
  },
};

export default apiClient;
