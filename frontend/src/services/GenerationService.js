import apiClient from './apiClient';

/**
 * @typedef {Object} GenerationRequest
 * @property {string} clipId - Clip ID to generate content for
 * @property {string} type - Generation type (image/video)
 * @property {string} [prompt] - Generation prompt
 * @property {Object} [parameters] - Generation parameters
 */

/**
 * @typedef {Object} BatchGenerationRequest
 * @property {string[]} clipIds - Array of clip IDs
 * @property {string} type - Generation type (image/video)
 * @property {Object} [parameters] - Generation parameters
 */

/**
 * @typedef {Object} GenerationResponse
 * @property {string} jobId - Job ID
 * @property {string} status - Job status
 * @property {string} [resultUrl] - Result URL when complete
 */

/**
 * Service for managing content generation
 */
class GenerationService {
  /**
   * Generate image or video content for a clip
   * @param {GenerationRequest} request - Generation request
   * @returns {Promise<GenerationResponse>} Generation response
   */
  async generate(request) {
    return apiClient.post('/generate', request);
  }

  /**
   * Generate content for multiple clips in batch
   * @param {BatchGenerationRequest} request - Batch generation request
   * @returns {Promise<Object>} Batch generation status
   */
  async generateBatch(request) {
    return apiClient.post('/generate/batch', request);
  }

  /**
   * Get status of a batch generation job
   * @param {string} batchId - Batch ID
   * @returns {Promise<Object>} Batch status
   */
  async getBatchStatus(batchId) {
    return apiClient.get(`/generate/batch/${batchId}`);
  }

  /**
   * List all batch generation jobs
   * @returns {Promise<Object>} List of batches
   */
  async listBatches() {
    return apiClient.get('/generate/batches');
  }
}

export default new GenerationService();
