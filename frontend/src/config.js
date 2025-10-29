class Config {
    constructor() {
        this.isDevelopment = process.env.NODE_ENV === 'development';
        this.backendUrl = this.getBackendUrl();
        this.validateConfig();
    }

    getBackendUrl() {
        // Explicit environment variable (highest priority)
        if (process.env.REACT_APP_BACKEND_URL) {
            return process.env.REACT_APP_BACKEND_URL;
        }

        // Development default
        if (this.isDevelopment) {
            return 'http://localhost:8001';
        }

        // Production MUST have explicit config
        console.error(
            'CRITICAL: REACT_APP_BACKEND_URL not set in production. ' +
            'API calls will fail. Please set this in your .env file or build configuration.'
        );

        // Return a placeholder that will clearly fail
        return 'BACKEND_URL_NOT_CONFIGURED';
    }

    validateConfig() {
        if (!this.isDevelopment && this.backendUrl === 'BACKEND_URL_NOT_CONFIGURED') {
            // In production, show a prominent error
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #dc2626;
                color: white;
                padding: 1rem;
                text-align: center;
                z-index: 9999;
                font-weight: bold;
            `;
            errorDiv.textContent = '⚠️ Configuration Error: Backend URL not set. Please contact administrator.';

            // Wait for DOM to be ready
            if (document.body) {
                document.body.appendChild(errorDiv);
            } else {
                document.addEventListener('DOMContentLoaded', () => {
                    document.body.appendChild(errorDiv);
                });
            }
        }
    }

    get apiUrl() {
        return `${this.backendUrl}/api/v1`;
    }
    
    // Legacy API URL (deprecated, for migration purposes only)
    get legacyApiUrl() {
        return `${this.backendUrl}/api`;
    }
}

export const config = new Config();
export const API = config.apiUrl;
