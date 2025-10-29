// Utility for managing persistent generation settings
const STORAGE_KEYS = {
  SELECTED_SERVER: 'emergent_storyboard_selected_server',
  SELECTED_MODEL: 'emergent_storyboard_selected_model',
  SELECTED_MODELS: 'emergent_storyboard_selected_models',
  USE_MULTIPLE_MODELS: 'emergent_storyboard_use_multiple_models',
  PROVIDER: 'emergent_storyboard_provider',
  SELECTED_PRESET: 'emergent_storyboard_selected_preset',
  GENERATION_PARAMS: 'emergent_storyboard_generation_params',
  ADVANCED_PARAMS: 'emergent_storyboard_advanced_params',
  LORAS: 'emergent_storyboard_loras',
  ACTIVE_TAB: 'emergent_storyboard_active_tab'
};

// Default settings
const DEFAULT_SETTINGS = {
  selectedServer: '',
  selectedModel: '',
  selectedModels: [],
  useMultipleModels: false,
  provider: 'comfyui',
  selectedPreset: 'fast',
  generationParams: {
    steps: 20,
    cfg: 7.0,
    width: 1024,
    height: 1024,
    seed: -1,
    sampler: 'euler',
    scheduler: 'normal',
    // Video-specific parameters
    video_fps: 24,
    video_frames: 14,
    motion_bucket_id: 127
  },
  advancedParams: {
    // Refiner
    use_refiner: false,
    refiner_model: '',
    refiner_switch: 0.8,
    
    // Face processing
    use_reactor: false,
    reactor_face_image: '',
    use_faceswap: false,
    
    // Upscaling
    use_upscale: false,
    upscale_factor: 2.0,
    upscale_model: 'RealESRGAN_x2plus',
    
    // Advanced settings
    pag_scale: 0.0, // Perturbed-Attention Guidance Scale
    clip_skip: 1,
    
    // ComfyUI workflow
    use_custom_workflow: false,
    workflow_json: ''
  },
  loras: [{ name: 'none', weight: 1.0 }],
  activeTab: 'image'
};

// Save settings to localStorage
export const saveGenerationSettings = (settings) => {
  try {
    Object.keys(settings).forEach(key => {
      if (STORAGE_KEYS[key]) {
        const value = settings[key];
        if (typeof value === 'object' && value !== null) {
          localStorage.setItem(STORAGE_KEYS[key], JSON.stringify(value));
        } else {
          localStorage.setItem(STORAGE_KEYS[key], value);
        }
      }
    });
  } catch (error) {
    console.warn('Failed to save generation settings:', error);
  }
};

// Load settings from localStorage
export const loadGenerationSettings = () => {
  const settings = { ...DEFAULT_SETTINGS };
  
  try {
    Object.keys(STORAGE_KEYS).forEach(storageKey => {
      const settingKey = Object.keys(STORAGE_KEYS).find(key => STORAGE_KEYS[key] === storageKey);
      if (settingKey) {
        const storedValue = localStorage.getItem(storageKey);
        if (storedValue) {
          // Try to parse as JSON first, fall back to string if that fails
          try {
            settings[settingKey] = JSON.parse(storedValue);
          } catch {
            settings[settingKey] = storedValue;
          }
        }
      }
    });
  } catch (error) {
    console.warn('Failed to load generation settings:', error);
  }
  
  return settings;
};

// Clear all stored settings
export const clearGenerationSettings = () => {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.warn('Failed to clear generation settings:', error);
  }
};

// Get model-specific settings
export const getModelSettings = (modelName) => {
  const allSettings = loadGenerationSettings();
  const modelSpecificKey = `emergent_storyboard_model_settings_${modelName}`;
  
  try {
    const storedModelSettings = localStorage.getItem(modelSpecificKey);
    if (storedModelSettings) {
      return JSON.parse(storedModelSettings);
    }
  } catch (error) {
    console.warn(`Failed to load model settings for ${modelName}:`, error);
  }
  
  return null;
};

// Save model-specific settings
export const saveModelSettings = (modelName, settings) => {
  const modelSpecificKey = `emergent_storyboard_model_settings_${modelName}`;
  
  try {
    localStorage.setItem(modelSpecificKey, JSON.stringify(settings));
  } catch (error) {
    console.warn(`Failed to save model settings for ${modelName}:`, error);
  }
};

// Merge model-specific settings with current settings
export const applyModelSettings = (modelName, currentSettings) => {
  const modelSettings = getModelSettings(modelName);
  if (modelSettings) {
    return {
      ...currentSettings,
      ...modelSettings
    };
  }
  return currentSettings;
};
