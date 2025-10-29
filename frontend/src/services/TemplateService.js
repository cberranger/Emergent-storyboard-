import apiClient from './apiClient';

/**
 * @typedef {Object} TemplateData
 * @property {string} name - Template name
 * @property {string} [description] - Template description
 * @property {string} [projectId] - Parent project ID
 * @property {Object} [style] - Style settings
 * @property {Object} [parameters] - Generation parameters
 * @property {string} [category] - Template category
 */

/**
 * @typedef {Object} Template
 * @property {string} id - Template ID
 * @property {string} name - Template name
 * @property {string} [description] - Template description
 * @property {string} [projectId] - Parent project ID
 * @property {Object} [style] - Style settings
 * @property {Object} [parameters] - Generation parameters
 * @property {string} [category] - Template category
 * @property {number} [useCount] - Usage count
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Update timestamp
 */

/**
 * Service for managing style templates
 */
class TemplateService {
  /**
   * Create a new style template
   * @param {TemplateData} templateData - Template data
   * @returns {Promise<Template>} Created template
   */
  async createTemplate(templateData) {
    return apiClient.post('/style-templates', templateData);
  }

  /**
   * Get all style templates, optionally filtered by project
   * @param {string} [projectId] - Optional project ID filter
   * @returns {Promise<Template[]>} List of templates
   */
  async listTemplates(projectId) {
    const params = projectId ? `?project_id=${projectId}` : '';
    return apiClient.get(`/style-templates${params}`);
  }

  /**
   * Get a specific style template by ID
   * @param {string} templateId - Template ID
   * @returns {Promise<Template>} Template details
   */
  async getTemplate(templateId) {
    return apiClient.get(`/style-templates/${templateId}`);
  }

  /**
   * Update a style template
   * @param {string} templateId - Template ID
   * @param {Partial<TemplateData>} templateData - Updated template data
   * @returns {Promise<Template>} Updated template
   */
  async updateTemplate(templateId, templateData) {
    return apiClient.put(`/style-templates/${templateId}`, templateData);
  }

  /**
   * Delete a style template
   * @param {string} templateId - Template ID
   * @returns {Promise<{message: string}>} Success message
   */
  async deleteTemplate(templateId) {
    return apiClient.delete(`/style-templates/${templateId}`);
  }

  /**
   * Increment use count for a template
   * @param {string} templateId - Template ID
   * @returns {Promise<{message: string}>} Success message
   */
  async useTemplate(templateId) {
    return apiClient.post(`/style-templates/${templateId}/use`);
  }
}

export default new TemplateService();
