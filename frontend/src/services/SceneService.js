import apiClient from './apiClient';

/**
 * @typedef {Object} SceneData
 * @property {string} projectId - Parent project ID
 * @property {string} name - Scene name
 * @property {string} [description] - Scene description
 * @property {number} [duration] - Scene duration in seconds
 * @property {number} [order] - Scene order
 */

/**
 * @typedef {Object} Scene
 * @property {string} id - Scene ID
 * @property {string} projectId - Parent project ID
 * @property {string} name - Scene name
 * @property {string} [description] - Scene description
 * @property {number} [duration] - Scene duration in seconds
 * @property {number} [order] - Scene order
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Update timestamp
 */

/**
 * Service for managing scenes
 */
class SceneService {
  /**
   * Create a new scene
   * @param {SceneData} sceneData - Scene data
   * @returns {Promise<Scene>} Created scene
   */
  async createScene(sceneData) {
    return apiClient.post('/scenes', sceneData);
  }

  /**
   * Get all scenes for a project
   * @param {string} projectId - Project ID
   * @returns {Promise<Scene[]>} List of scenes
   */
  async listScenesByProject(projectId) {
    return apiClient.get(`/scenes/project/${projectId}`);
  }

  /**
   * Get a specific scene by ID
   * @param {string} sceneId - Scene ID
   * @returns {Promise<Scene>} Scene details
   */
  async getScene(sceneId) {
    return apiClient.get(`/scenes/${sceneId}`);
  }

  /**
   * Update a scene
   * @param {string} sceneId - Scene ID
   * @param {Partial<SceneData>} sceneData - Updated scene data
   * @returns {Promise<Scene>} Updated scene
   */
  async updateScene(sceneId, sceneData) {
    return apiClient.put(`/scenes/${sceneId}`, sceneData);
  }

  /**
   * Delete a scene
   * @param {string} sceneId - Scene ID
   * @returns {Promise<{message: string}>} Success message
   */
  async deleteScene(sceneId) {
    return apiClient.delete(`/scenes/${sceneId}`);
  }

  /**
   * Analyze scene timeline for overlaps and gaps
   * @param {string} sceneId - Scene ID
   * @returns {Promise<Object>} Timeline analysis results
   */
  async analyzeTimeline(sceneId) {
    return apiClient.get(`/scenes/${sceneId}/timeline-analysis`);
  }
}

export default new SceneService();
