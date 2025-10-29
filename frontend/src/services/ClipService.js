import apiClient from './apiClient';

/**
 * @typedef {Object} ClipData
 * @property {string} sceneId - Parent scene ID
 * @property {string} name - Clip name
 * @property {string} [description] - Clip description
 * @property {number} [position] - Timeline position in seconds
 * @property {number} [duration] - Clip duration in seconds
 * @property {string} [imagePrompt] - Image generation prompt
 * @property {string} [videoPrompt] - Video generation prompt
 * @property {string} [type] - Clip type (image/video)
 */

/**
 * @typedef {Object} Clip
 * @property {string} id - Clip ID
 * @property {string} sceneId - Parent scene ID
 * @property {string} name - Clip name
 * @property {string} [description] - Clip description
 * @property {number} [position] - Timeline position in seconds
 * @property {number} [duration] - Clip duration in seconds
 * @property {string} [imagePrompt] - Image generation prompt
 * @property {string} [videoPrompt] - Video generation prompt
 * @property {string} [type] - Clip type
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Update timestamp
 */

/**
 * Service for managing clips
 */
class ClipService {
  /**
   * Create a new clip
   * @param {ClipData} clipData - Clip data
   * @returns {Promise<Clip>} Created clip
   */
  async createClip(clipData) {
    return apiClient.post('/clips', clipData);
  }

  /**
   * Get all clips for a scene
   * @param {string} sceneId - Scene ID
   * @returns {Promise<Clip[]>} List of clips
   */
  async listClipsByScene(sceneId) {
    return apiClient.get(`/clips/scene/${sceneId}`);
  }

  /**
   * Get a specific clip by ID
   * @param {string} clipId - Clip ID
   * @returns {Promise<Clip>} Clip details
   */
  async getClip(clipId) {
    return apiClient.get(`/clips/${clipId}`);
  }

  /**
   * Get clip gallery with all generated content
   * @param {string} clipId - Clip ID
   * @returns {Promise<Object>} Clip gallery data
   */
  async getClipGallery(clipId) {
    return apiClient.get(`/clips/${clipId}/gallery`);
  }

  /**
   * Update a clip
   * @param {string} clipId - Clip ID
   * @param {Partial<ClipData>} clipData - Updated clip data
   * @returns {Promise<Clip>} Updated clip
   */
  async updateClip(clipId, clipData) {
    return apiClient.put(`/clips/${clipId}`, clipData);
  }

  /**
   * Update clip timeline position
   * @param {string} clipId - Clip ID
   * @param {number} position - New timeline position in seconds
   * @param {boolean} [checkOverlap=true] - Whether to check for overlaps
   * @returns {Promise<Object>} Update result
   */
  async updateClipTimelinePosition(clipId, position, checkOverlap = true) {
    return apiClient.put(
      `/clips/${clipId}/timeline-position?check_overlap=${checkOverlap}`,
      { position }
    );
  }

  /**
   * Update clip prompts
   * @param {string} clipId - Clip ID
   * @param {string} [imagePrompt=''] - Image generation prompt
   * @param {string} [videoPrompt=''] - Video generation prompt
   * @returns {Promise<Object>} Update result
   */
  async updateClipPrompts(clipId, imagePrompt = '', videoPrompt = '') {
    return apiClient.put(
      `/clips/${clipId}/prompts?image_prompt=${encodeURIComponent(imagePrompt)}&video_prompt=${encodeURIComponent(videoPrompt)}`
    );
  }

  /**
   * Delete a clip
   * @param {string} clipId - Clip ID
   * @returns {Promise<{message: string}>} Success message
   */
  async deleteClip(clipId) {
    return apiClient.delete(`/clips/${clipId}`);
  }
}

export default new ClipService();
