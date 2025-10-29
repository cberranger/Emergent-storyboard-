import apiClient from './apiClient';

/**
 * @typedef {Object} QueueJobRequest
 * @property {string} clipId - Clip ID
 * @property {string} type - Job type (image/video)
 * @property {number} [priority] - Job priority (higher = more important)
 * @property {Object} [parameters] - Generation parameters
 */

/**
 * @typedef {Object} QueueJob
 * @property {string} id - Job ID
 * @property {string} clipId - Clip ID
 * @property {string} type - Job type
 * @property {string} status - Job status
 * @property {number} [priority] - Job priority
 * @property {string} [resultUrl] - Result URL when complete
 * @property {string} [error] - Error message if failed
 * @property {string} createdAt - Creation timestamp
 */

/**
 * @typedef {Object} ServerRegistration
 * @property {string} url - Server URL
 * @property {string[]} capabilities - Server capabilities
 * @property {Object} [resources] - Resource availability
 */

/**
 * Service for managing generation queue
 */
class QueueService {
  /**
   * Add a generation job to the queue
   * @param {QueueJobRequest} jobRequest - Job request data
   * @returns {Promise<QueueJob>} Created job
   */
  async addJob(jobRequest) {
    return apiClient.post('/queue/jobs', jobRequest);
  }

  /**
   * Get all queued jobs with optional status filter
   * @param {string} [status] - Optional status filter
   * @returns {Promise<QueueJob[]>} List of jobs
   */
  async getAllJobs(status) {
    const params = status ? `?status=${status}` : '';
    return apiClient.get(`/queue/jobs${params}`);
  }

  /**
   * Get overall queue status
   * @returns {Promise<Object>} Queue status
   */
  async getQueueStatus() {
    return apiClient.get('/queue/status');
  }

  /**
   * Get status of a specific job
   * @param {string} jobId - Job ID
   * @returns {Promise<QueueJob>} Job details
   */
  async getJobStatus(jobId) {
    return apiClient.get(`/queue/jobs/${jobId}`);
  }

  /**
   * Get all queued jobs for a project
   * @param {string} projectId - Project ID
   * @returns {Promise<Object>} Project queue data
   */
  async getProjectQueue(projectId) {
    return apiClient.get(`/queue/projects/${projectId}/jobs`);
  }

  /**
   * Register a server with the queue manager
   * @param {string} serverId - Server ID
   * @param {ServerRegistration} registration - Server registration data
   * @returns {Promise<{message: string}>} Success message
   */
  async registerServer(serverId, registration) {
    return apiClient.post(`/queue/servers/${serverId}/register`, registration);
  }

  /**
   * Get the next job for a server to process
   * @param {string} serverId - Server ID
   * @returns {Promise<QueueJob|null>} Next job or null if none available
   */
  async getNextJob(serverId) {
    return apiClient.get(`/queue/servers/${serverId}/next`);
  }

  /**
   * Mark a job as completed
   * @param {string} jobId - Job ID
   * @param {boolean} success - Whether job succeeded
   * @param {string} [resultUrl] - Result URL if successful
   * @param {string} [error] - Error message if failed
   * @returns {Promise<{message: string}>} Success message
   */
  async completeJob(jobId, success, resultUrl, error) {
    const params = new URLSearchParams({
      success: success.toString(),
      ...(resultUrl && { result_url: resultUrl }),
      ...(error && { error }),
    });
    return apiClient.post(`/queue/jobs/${jobId}/complete?${params.toString()}`);
  }
}

export default new QueueService();
