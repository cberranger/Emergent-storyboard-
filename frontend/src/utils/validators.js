/**
 * Frontend validation utilities
 * Validates data before sending to API
 */

/**
 * Check if string is a valid UUID v4
 * @param {string} str - String to validate
 * @returns {boolean} - True if valid UUID
 */
export const isValidUUID = (str) => {
  if (!str || typeof str !== 'string') return false;
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
};

/**
 * Check if value is a valid positive number
 * @param {any} value - Value to validate
 * @returns {boolean} - True if valid positive number
 */
export const isPositiveNumber = (value) => {
  const num = Number(value);
  return !isNaN(num) && num > 0 && isFinite(num);
};

/**
 * Check if value is a valid non-negative number
 * @param {any} value - Value to validate
 * @returns {boolean} - True if valid non-negative number
 */
export const isNonNegativeNumber = (value) => {
  const num = Number(value);
  return !isNaN(num) && num >= 0 && isFinite(num);
};

/**
 * Check if string is not empty
 * @param {string} str - String to validate
 * @returns {boolean} - True if non-empty string
 */
export const isNonEmptyString = (str) => {
  return typeof str === 'string' && str.trim().length > 0;
};

/**
 * Validate project ID
 * @param {string} projectId - Project ID to validate
 * @throws {Error} - If invalid
 */
export const validateProjectId = (projectId) => {
  if (!isValidUUID(projectId)) {
    throw new Error('Invalid project ID format');
  }
};

/**
 * Validate scene ID
 * @param {string} sceneId - Scene ID to validate
 * @throws {Error} - If invalid
 */
export const validateSceneId = (sceneId) => {
  if (!isValidUUID(sceneId)) {
    throw new Error('Invalid scene ID format');
  }
};

/**
 * Validate clip ID
 * @param {string} clipId - Clip ID to validate
 * @throws {Error} - If invalid
 */
export const validateClipId = (clipId) => {
  if (!isValidUUID(clipId)) {
    throw new Error('Invalid clip ID format');
  }
};

/**
 * Validate server ID
 * @param {string} serverId - Server ID to validate
 * @throws {Error} - If invalid
 */
export const validateServerId = (serverId) => {
  if (!isValidUUID(serverId)) {
    throw new Error('Invalid server ID format');
  }
};

/**
 * Validate timeline position
 * @param {number} position - Position in seconds
 * @throws {Error} - If invalid
 */
export const validateTimelinePosition = (position) => {
  if (!isNonNegativeNumber(position)) {
    throw new Error('Timeline position must be a non-negative number');
  }
  if (position > 10000) {
    throw new Error('Timeline position exceeds maximum (10000 seconds)');
  }
};

/**
 * Validate clip length
 * @param {number} length - Length in seconds
 * @throws {Error} - If invalid
 */
export const validateClipLength = (length) => {
  if (!isPositiveNumber(length)) {
    throw new Error('Clip length must be a positive number');
  }
  if (length > 300) {
    throw new Error('Clip length exceeds maximum (300 seconds)');
  }
};

/**
 * Validate file size
 * @param {File} file - File object
 * @param {number} maxSizeMB - Maximum size in MB
 * @throws {Error} - If file too large
 */
export const validateFileSize = (file, maxSizeMB) => {
  if (!file) {
    throw new Error('No file provided');
  }
  const maxBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxBytes) {
    throw new Error(`File size exceeds maximum of ${maxSizeMB}MB`);
  }
};

/**
 * Validate file type
 * @param {File} file - File object
 * @param {string[]} allowedTypes - Allowed MIME types
 * @throws {Error} - If file type not allowed
 */
export const validateFileType = (file, allowedTypes) => {
  if (!file) {
    throw new Error('No file provided');
  }
  if (!allowedTypes.includes(file.type)) {
    throw new Error(`Invalid file type. Allowed: ${allowedTypes.join(', ')}`);
  }
};

/**
 * Validate music file
 * @param {File} file - File object
 * @throws {Error} - If invalid
 */
export const validateMusicFile = (file) => {
  const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3'];
  validateFileType(file, allowedTypes);
  validateFileSize(file, 50); // 50MB
};

/**
 * Validate image file
 * @param {File} file - File object
 * @throws {Error} - If invalid
 */
export const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  validateFileType(file, allowedTypes);
  validateFileSize(file, 10); // 10MB
};

/**
 * Sanitize string for safe display
 * @param {string} str - String to sanitize
 * @returns {string} - Sanitized string
 */
export const sanitizeString = (str) => {
  if (typeof str !== 'string') return '';
  // Remove or escape potentially dangerous characters
  return str
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

/**
 * Validate and sanitize user input
 * @param {string} input - User input
 * @param {number} maxLength - Maximum length
 * @returns {string} - Sanitized input
 * @throws {Error} - If invalid
 */
export const validateAndSanitizeInput = (input, maxLength = 1000) => {
  if (!isNonEmptyString(input)) {
    throw new Error('Input cannot be empty');
  }
  if (input.length > maxLength) {
    throw new Error(`Input exceeds maximum length of ${maxLength} characters`);
  }
  return sanitizeString(input);
};

/**
 * Sanitize input (alias for sanitizeString for consistency)
 * @param {string} input - Input to sanitize
 * @returns {string} - Sanitized input
 */
export const sanitizeInput = (input) => {
  return sanitizeString(input);
};

/**
 * Validate prompt length
 * @param {string} prompt - Prompt text
 * @param {number} maxLength - Maximum length (default 2000)
 * @throws {Error} - If prompt too long or empty
 */
export const validatePromptLength = (prompt, maxLength = 2000) => {
  if (!prompt || typeof prompt !== 'string') {
    throw new Error('Prompt must be a non-empty string');
  }

  const trimmed = prompt.trim();
  if (trimmed.length === 0) {
    throw new Error('Prompt cannot be empty');
  }

  if (trimmed.length > maxLength) {
    throw new Error(`Prompt exceeds maximum length of ${maxLength} characters (current: ${trimmed.length})`);
  }
};

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @throws {Error} - If URL invalid
 */
export const validateURL = (url) => {
  if (!url || typeof url !== 'string') {
    throw new Error('URL must be a non-empty string');
  }

  try {
    const urlObj = new URL(url);

    // Only allow http and https protocols
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      throw new Error('URL must use HTTP or HTTPS protocol');
    }

    // Check for valid hostname
    if (!urlObj.hostname || urlObj.hostname === '') {
      throw new Error('URL must have a valid hostname');
    }

  } catch (e) {
    if (e.message.includes('protocol') || e.message.includes('hostname')) {
      throw e; // Re-throw our custom errors
    }
    throw new Error('Invalid URL format');
  }
};

/**
 * Validate generation parameters
 * @param {Object} params - Generation parameters
 * @throws {Error} - If parameters invalid
 */
export const validateGenerationParams = (params) => {
  if (!params || typeof params !== 'object') {
    throw new Error('Parameters must be an object');
  }

  // Validate steps (typically 1-150)
  if (params.steps !== undefined) {
    const steps = Number(params.steps);
    if (isNaN(steps) || steps < 1 || steps > 150) {
      throw new Error('Steps must be between 1 and 150');
    }
  }

  // Validate cfg_scale (typically 1-30)
  if (params.cfg_scale !== undefined) {
    const cfg = Number(params.cfg_scale);
    if (isNaN(cfg) || cfg < 1 || cfg > 30) {
      throw new Error('CFG scale must be between 1 and 30');
    }
  }

  // Validate width (must be multiple of 8, typically 256-2048)
  if (params.width !== undefined) {
    const width = Number(params.width);
    if (isNaN(width) || width < 256 || width > 2048 || width % 8 !== 0) {
      throw new Error('Width must be between 256-2048 and divisible by 8');
    }
  }

  // Validate height (must be multiple of 8, typically 256-2048)
  if (params.height !== undefined) {
    const height = Number(params.height);
    if (isNaN(height) || height < 256 || height > 2048 || height % 8 !== 0) {
      throw new Error('Height must be between 256-2048 and divisible by 8');
    }
  }

  // Validate seed (-1 for random, or 0 to 4294967295)
  if (params.seed !== undefined) {
    const seed = Number(params.seed);
    if (isNaN(seed) || (seed !== -1 && (seed < 0 || seed > 4294967295))) {
      throw new Error('Seed must be -1 (random) or between 0 and 4294967295');
    }
  }

  // Validate denoise (0-1)
  if (params.denoise !== undefined) {
    const denoise = Number(params.denoise);
    if (isNaN(denoise) || denoise < 0 || denoise > 1) {
      throw new Error('Denoise must be between 0 and 1');
    }
  }

  // Validate sampler_name (string, non-empty if provided)
  if (params.sampler_name !== undefined && params.sampler_name !== null) {
    if (typeof params.sampler_name !== 'string' || params.sampler_name.trim() === '') {
      throw new Error('Sampler name must be a non-empty string');
    }
  }

  // Validate scheduler (string, non-empty if provided)
  if (params.scheduler !== undefined && params.scheduler !== null) {
    if (typeof params.scheduler !== 'string' || params.scheduler.trim() === '') {
      throw new Error('Scheduler must be a non-empty string');
    }
  }
};
