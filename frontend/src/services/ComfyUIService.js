import apiClient from './apiClient';

/**
 * @typedef {Object} ServerData
 * @property {string} name - Server name
 * @property {string} url - Server URL
 * @property {boolean} [isActive] - Whether server is active
 * @property {Object} [capabilities] - Server capabilities
 */

/**
 * @typedef {Object} ComfyUIServer
 * @property {string} id - Server ID
 * @property {string} name - Server name
 * @property {string} url - Server URL
 * @property {boolean} isActive - Whether server is active
 * @property {Object} [capabilities] - Server capabilities
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Update timestamp
 */

/**
 * Service for managing ComfyUI servers
 */
class ComfyUIService {
  /**
   * Register a new ComfyUI server
   * @param {ServerData} serverData - Server data
   * @returns {Promise<ComfyUIServer>} Created server
   */
  async createServer(serverData) {
    return apiClient.post('/comfyui/servers', serverData);
  }

  /**
   * Get all registered ComfyUI servers
   * @returns {Promise<ComfyUIServer[]>} List of servers
   */
  async listServers() {
    return apiClient.get('/comfyui/servers');
  }

  /**
   * Get detailed information about a ComfyUI server
   * @param {string} serverId - Server ID
   * @returns {Promise<Object>} Server information including models and status
   */
  async getServerInfo(serverId) {
    return apiClient.get(`/comfyui/servers/${serverId}/info`);
  }

  /**
   * Update a ComfyUI server configuration
   * @param {string} serverId - Server ID
   * @param {ServerData} serverData - Updated server data
   * @returns {Promise<ComfyUIServer>} Updated server
   */
  async updateServer(serverId, serverData) {
    return apiClient.put(`/comfyui/servers/${serverId}`, serverData);
  }

  /**
   * Delete a ComfyUI server
   * @param {string} serverId - Server ID
   * @returns {Promise<{message: string}>} Success message
   */
  async deleteServer(serverId) {
    return apiClient.delete(`/comfyui/servers/${serverId}`);
  }
}

export default new ComfyUIService();
