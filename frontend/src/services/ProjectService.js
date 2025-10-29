import apiClient from './apiClient';

/**
 * @typedef {Object} ProjectData
 * @property {string} name - Project name
 * @property {string} [description] - Project description
 * @property {Object} [settings] - Project settings
 */

/**
 * @typedef {Object} Project
 * @property {string} id - Project ID
 * @property {string} name - Project name
 * @property {string} [description] - Project description
 * @property {Object} [settings] - Project settings
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Update timestamp
 */

/**
 * Service for managing projects
 */
class ProjectService {
  /**
   * Create a new project
   * @param {ProjectData} projectData - Project data
   * @returns {Promise<Project>} Created project
   */
  async createProject(projectData) {
    return apiClient.post('/projects', projectData);
  }

  /**
   * Get all projects
   * @returns {Promise<Project[]>} List of projects
   */
  async listProjects() {
    return apiClient.get('/projects');
  }

  /**
   * Get a specific project by ID
   * @param {string} projectId - Project ID
   * @returns {Promise<Project>} Project details
   */
  async getProject(projectId) {
    return apiClient.get(`/projects/${projectId}`);
  }

  /**
   * Get a project with all its scenes
   * @param {string} projectId - Project ID
   * @returns {Promise<Object>} Project with scenes
   */
  async getProjectWithScenes(projectId) {
    return apiClient.get(`/projects/${projectId}/with-scenes`);
  }

  /**
   * Update a project
   * @param {string} projectId - Project ID
   * @param {Partial<ProjectData>} projectData - Updated project data
   * @returns {Promise<Project>} Updated project
   */
  async updateProject(projectId, projectData) {
    return apiClient.put(`/projects/${projectId}`, projectData);
  }

  /**
   * Delete a project
   * @param {string} projectId - Project ID
   * @returns {Promise<{message: string}>} Success message
   */
  async deleteProject(projectId) {
    return apiClient.delete(`/projects/${projectId}`);
  }

  /**
   * Get all clips for a project
   * @param {string} projectId - Project ID
   * @returns {Promise<Array>} List of clips
   */
  async getProjectClips(projectId) {
    return apiClient.get(`/projects/${projectId}/clips`);
  }
}

export default new ProjectService();
