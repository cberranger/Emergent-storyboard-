import apiClient from './api';

const resultCache = new Map();
const pollingIntervals = new Map();

export const faceFusionService = {
  getStatus: async (params) => {
    const response = await apiClient.get('/facefusion/status', { params });
    return response.data;
  },

  enhanceFace: async (data) => {
    const response = await apiClient.post('/facefusion/enhance-face', data);
    return response.data;
  },

  adjustFaceAge: async (data) => {
    const response = await apiClient.post('/facefusion/adjust-face-age', data);
    return response.data;
  },

  swapFace: async (data) => {
    const response = await apiClient.post('/facefusion/swap-face', data);
    return response.data;
  },

  batchProcess: async (data) => {
    const response = await apiClient.post('/facefusion/batch-process', data);
    return response.data;
  },

  detectFaces: async (data) => {
    const response = await apiClient.post('/facefusion/detect-faces', data);
    return response.data;
  },

  selectFace: async (data) => {
    const response = await apiClient.post('/facefusion/select-face', data);
    return response.data;
  },

  getFaceAnalysis: async (imageId, faceIndex) => {
    const response = await apiClient.get(`/facefusion/faces/${imageId}/${faceIndex}/analysis`);
    return response.data;
  },

  setFaceMask: async (data) => {
    const response = await apiClient.post('/facefusion/mask/set', data);
    return response.data;
  },

  adjustMask: async (data) => {
    const response = await apiClient.post('/facefusion/mask/adjust', data);
    return response.data;
  },

  generateMask: async (data) => {
    const response = await apiClient.post('/facefusion/mask/generate', data);
    return response.data;
  },

  getMaskPreview: async (maskId) => {
    const response = await apiClient.get(`/facefusion/mask/${maskId}/preview`);
    return response.data;
  },

  processMultipleFaces: async (data) => {
    const response = await apiClient.post('/facefusion/multi-face/process', data);
    return response.data;
  },

  mapFaces: async (data) => {
    const response = await apiClient.post('/facefusion/multi-face/map', data);
    return response.data;
  },

  setFaceProcessingMode: async (data) => {
    const response = await apiClient.post('/facefusion/multi-face/mode', data);
    return response.data;
  },

  configureEnhancement: async (data) => {
    const response = await apiClient.post('/facefusion/enhancement/configure', data);
    return response.data;
  },

  applyAdvancedEnhancement: async (data) => {
    const response = await apiClient.post('/facefusion/enhancement/apply', data);
    return response.data;
  },

  getEnhancementPresets: async () => {
    const response = await apiClient.get('/facefusion/enhancement/presets');
    return response.data;
  },

  saveEnhancementPreset: async (data) => {
    const response = await apiClient.post('/facefusion/enhancement/presets', data);
    return response.data;
  },

  editFaceFeatures: async (data) => {
    const response = await apiClient.post('/facefusion/edit/features', data);
    return response.data;
  },

  adjustFaceExpression: async (data) => {
    const response = await apiClient.post('/facefusion/edit/expression', data);
    return response.data;
  },

  modifyFaceShape: async (data) => {
    const response = await apiClient.post('/facefusion/edit/shape', data);
    return response.data;
  },

  colorCorrectFace: async (data) => {
    const response = await apiClient.post('/facefusion/edit/color-correct', data);
    return response.data;
  },

  processVideo: async (data) => {
    const response = await apiClient.post('/facefusion/video/process', data);
    return response.data;
  },

  processVideoFrameRange: async (data) => {
    const response = await apiClient.post('/facefusion/video/process-range', data);
    return response.data;
  },

  extractVideoFrames: async (data) => {
    const response = await apiClient.post('/facefusion/video/extract-frames', data);
    return response.data;
  },

  getVideoProcessingProgress: async (jobId) => {
    const response = await apiClient.get(`/facefusion/video/progress/${jobId}`);
    return response.data;
  },

  renderVideo: async (data) => {
    const response = await apiClient.post('/facefusion/video/render', data);
    return response.data;
  },

  createJob: async (data) => {
    const response = await apiClient.post('/facefusion/jobs', data);
    return response.data;
  },

  getJob: async (jobId) => {
    const cacheKey = `job_${jobId}`;
    if (resultCache.has(cacheKey)) {
      const cached = resultCache.get(cacheKey);
      if (Date.now() - cached.timestamp < 5000) {
        return cached.data;
      }
    }

    const response = await apiClient.get(`/facefusion/jobs/${jobId}`);
    resultCache.set(cacheKey, { data: response.data, timestamp: Date.now() });
    return response.data;
  },

  getJobStatus: async (jobId) => {
    const response = await apiClient.get(`/facefusion/jobs/${jobId}/status`);
    return response.data;
  },

  cancelJob: async (jobId) => {
    const response = await apiClient.post(`/facefusion/jobs/${jobId}/cancel`);
    this.stopPolling(jobId);
    return response.data;
  },

  retryJob: async (jobId) => {
    const response = await apiClient.post(`/facefusion/jobs/${jobId}/retry`);
    return response.data;
  },

  getJobQueue: async (params) => {
    const response = await apiClient.get('/facefusion/jobs', { params });
    return response.data;
  },

  clearCompletedJobs: async () => {
    const response = await apiClient.delete('/facefusion/jobs/completed');
    return response.data;
  },

  getJobResult: async (jobId) => {
    const cacheKey = `result_${jobId}`;
    if (resultCache.has(cacheKey)) {
      const cached = resultCache.get(cacheKey);
      if (Date.now() - cached.timestamp < 60000) {
        return cached.data;
      }
    }

    const response = await apiClient.get(`/facefusion/jobs/${jobId}/result`);
    resultCache.set(cacheKey, { data: response.data, timestamp: Date.now() });
    return response.data;
  },

  downloadResult: async (jobId, format = 'original') => {
    const response = await apiClient.get(`/facefusion/jobs/${jobId}/download`, {
      params: { format },
      responseType: 'blob'
    });
    return response;
  },

  pollJobStatus: (jobId, onUpdate, options = {}) => {
    const {
      interval = 2000,
      timeout = 300000,
      onComplete,
      onError,
      onTimeout
    } = options;

    if (pollingIntervals.has(jobId)) {
      clearInterval(pollingIntervals.get(jobId).intervalId);
      clearTimeout(pollingIntervals.get(jobId).timeoutId);
    }

    const startTime = Date.now();

    const intervalId = setInterval(async () => {
      try {
        const status = await faceFusionService.getJobStatus(jobId);
        onUpdate(status);

        if (status.status === 'completed' || status.status === 'success') {
          faceFusionService.stopPolling(jobId);
          if (onComplete) {
            const result = await faceFusionService.getJobResult(jobId);
            onComplete(result);
          }
        } else if (status.status === 'failed' || status.status === 'error') {
          faceFusionService.stopPolling(jobId);
          if (onError) onError(status.error || 'Job failed');
        }
      } catch (error) {
        console.error('Polling error:', error);
        if (onError) onError(error);
      }
    }, interval);

    const timeoutId = setTimeout(() => {
      faceFusionService.stopPolling(jobId);
      if (onTimeout) onTimeout();
    }, timeout);

    pollingIntervals.set(jobId, { intervalId, timeoutId, startTime });

    return () => faceFusionService.stopPolling(jobId);
  },

  stopPolling: (jobId) => {
    if (pollingIntervals.has(jobId)) {
      const { intervalId, timeoutId } = pollingIntervals.get(jobId);
      clearInterval(intervalId);
      clearTimeout(timeoutId);
      pollingIntervals.delete(jobId);
    }
  },

  stopAllPolling: () => {
    pollingIntervals.forEach(({ intervalId, timeoutId }) => {
      clearInterval(intervalId);
      clearTimeout(timeoutId);
    });
    pollingIntervals.clear();
  },

  uploadSourceMedia: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options.mediaType) formData.append('media_type', options.mediaType);
    if (options.metadata) formData.append('metadata', JSON.stringify(options.metadata));

    const response = await apiClient.post('/facefusion/upload/source', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: options.onProgress,
    });
    return response.data;
  },

  uploadTargetMedia: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options.mediaType) formData.append('media_type', options.mediaType);
    if (options.metadata) formData.append('metadata', JSON.stringify(options.metadata));

    const response = await apiClient.post('/facefusion/upload/target', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: options.onProgress,
    });
    return response.data;
  },

  uploadMaskImage: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options.imageId) formData.append('image_id', options.imageId);

    const response = await apiClient.post('/facefusion/upload/mask', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: options.onProgress,
    });
    return response.data;
  },

  uploadBatch: async (files, options = {}) => {
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`files[${index}]`, file);
    });
    
    if (options.mediaType) formData.append('media_type', options.mediaType);

    const response = await apiClient.post('/facefusion/upload/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: options.onProgress,
    });
    return response.data;
  },

  getCachedResult: (jobId) => {
    const cacheKey = `result_${jobId}`;
    if (resultCache.has(cacheKey)) {
      const cached = resultCache.get(cacheKey);
      return cached.data;
    }
    return null;
  },

  cacheResult: (jobId, data) => {
    const cacheKey = `result_${jobId}`;
    resultCache.set(cacheKey, { data, timestamp: Date.now() });
  },

  clearCache: (jobId = null) => {
    if (jobId) {
      resultCache.delete(`job_${jobId}`);
      resultCache.delete(`result_${jobId}`);
    } else {
      resultCache.clear();
    }
  },

  getCacheStats: () => {
    return {
      size: resultCache.size,
      entries: Array.from(resultCache.keys()),
      activePolls: pollingIntervals.size,
      pollingJobs: Array.from(pollingIntervals.keys())
    };
  }
};
