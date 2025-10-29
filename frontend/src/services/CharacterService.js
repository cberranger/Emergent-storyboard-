import apiClient from './apiClient';

/**
 * @typedef {Object} CharacterData
 * @property {string} name - Character name
 * @property {string} [description] - Character description
 * @property {string} [projectId] - Parent project ID
 * @property {string} [imageUrl] - Reference image URL
 * @property {Object} [appearance] - Appearance settings
 * @property {Object} [generationSettings] - Generation parameters
 */

/**
 * @typedef {Object} Character
 * @property {string} id - Character ID
 * @property {string} name - Character name
 * @property {string} [description] - Character description
 * @property {string} [projectId] - Parent project ID
 * @property {string} [imageUrl] - Reference image URL
 * @property {Object} [appearance] - Appearance settings
 * @property {Object} [generationSettings] - Generation parameters
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Update timestamp
 */

/**
 * Service for managing characters
 */
class CharacterService {
  /**
   * Create a new character
   * @param {CharacterData} characterData - Character data
   * @returns {Promise<Character>} Created character
   */
  async createCharacter(characterData) {
    return apiClient.post('/characters', characterData);
  }

  /**
   * Get all characters, optionally filtered by project
   * @param {string} [projectId] - Optional project ID filter
   * @returns {Promise<Character[]>} List of characters
   */
  async listCharacters(projectId) {
    const params = projectId ? `?project_id=${projectId}` : '';
    return apiClient.get(`/characters${params}`);
  }

  /**
   * Get a specific character by ID
   * @param {string} characterId - Character ID
   * @returns {Promise<Character>} Character details
   */
  async getCharacter(characterId) {
    return apiClient.get(`/characters/${characterId}`);
  }

  /**
   * Update a character
   * @param {string} characterId - Character ID
   * @param {Partial<CharacterData>} characterData - Updated character data
   * @returns {Promise<Character>} Updated character
   */
  async updateCharacter(characterId, characterData) {
    return apiClient.put(`/characters/${characterId}`, characterData);
  }

  /**
   * Delete a character
   * @param {string} characterId - Character ID
   * @returns {Promise<{message: string}>} Success message
   */
  async deleteCharacter(characterId) {
    return apiClient.delete(`/characters/${characterId}`);
  }

  /**
   * Apply character settings to a clip's generation prompt
   * @param {string} characterId - Character ID
   * @param {string} clipId - Clip ID
   * @returns {Promise<Object>} Application result
   */
  async applyCharacterToClip(characterId, clipId) {
    return apiClient.post(`/characters/${characterId}/apply/${clipId}`);
  }
}

export default new CharacterService();
