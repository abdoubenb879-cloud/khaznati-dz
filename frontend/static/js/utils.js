/**
 * Khaznati DZ - Utility Functions
 * خزنتي - وظائف مساعدة
 */

// =============================================================================
// API HELPER
// =============================================================================

const API = {
    baseUrl: '/api',

    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Include cookies
        };

        // Add CSRF token for state-changing requests
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
            const csrfToken = await this.getCsrfToken();
            if (csrfToken) {
                defaultOptions.headers['X-CSRF-Token'] = csrfToken;
            }
        }

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new APIError(data.detail || 'حدث خطأ غير متوقع', response.status, data);
            }

            return data;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError('فشل الاتصال بالخادم', 0);
        }
    },

    /**
     * Get CSRF token
     * @returns {Promise<string|null>} CSRF token
     */
    async getCsrfToken() {
        try {
            const data = await this.request('/auth/csrf-token', { method: 'GET' });
            return data.csrf_token;
        } catch {
            return null;
        }
    },

    // Convenience methods
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    },

    put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },
};

/**
 * Custom API Error
 */
class APIError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}


// =============================================================================
// TOAST NOTIFICATIONS
// =============================================================================

const Toast = {
    container: null,

    /**
     * Initialize toast container
     */
    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    /**
     * Show a toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, error, warning, info)
     * @param {number} duration - Duration in ms (default 4000)
     */
    show(message, type = 'info', duration = 4000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ',
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="إغلاق">✕</button>
        `;

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.dismiss(toast);
        });

        this.container.appendChild(toast);

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => this.dismiss(toast), duration);
        }

        return toast;
    },

    /**
     * Dismiss a toast
     * @param {HTMLElement} toast - Toast element
     */
    dismiss(toast) {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    },

    // Convenience methods
    success(message, duration) { return this.show(message, 'success', duration); },
    error(message, duration) { return this.show(message, 'error', duration); },
    warning(message, duration) { return this.show(message, 'warning', duration); },
    info(message, duration) { return this.show(message, 'info', duration); },
};


// =============================================================================
// LOADING STATE
// =============================================================================

const Loading = {
    overlay: null,

    /**
     * Show loading overlay
     */
    show() {
        if (!this.overlay) {
            this.overlay = document.getElementById('loading-overlay');
        }
        if (this.overlay) {
            this.overlay.classList.remove('hidden');
        }
    },

    /**
     * Hide loading overlay
     */
    hide() {
        if (!this.overlay) {
            this.overlay = document.getElementById('loading-overlay');
        }
        if (this.overlay) {
            this.overlay.classList.add('hidden');
        }
    },
};


// =============================================================================
// FORM HELPERS
// =============================================================================

const Form = {
    /**
     * Get form data as object
     * @param {HTMLFormElement} form - Form element
     * @returns {Object} Form data
     */
    getData(form) {
        const formData = new FormData(form);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    },

    /**
     * Set form errors
     * @param {HTMLFormElement} form - Form element
     * @param {Object} errors - Field errors
     */
    setErrors(form, errors) {
        // Clear existing errors
        form.querySelectorAll('.form-input.error').forEach(input => {
            input.classList.remove('error');
        });
        form.querySelectorAll('.form-error').forEach(error => {
            error.remove();
        });

        // Set new errors
        for (const [field, message] of Object.entries(errors)) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('error');
                const errorEl = document.createElement('div');
                errorEl.className = 'form-error';
                errorEl.textContent = message;
                input.parentNode.insertBefore(errorEl, input.nextSibling);
            }
        }
    },

    /**
     * Clear form errors
     * @param {HTMLFormElement} form - Form element
     */
    clearErrors(form) {
        form.querySelectorAll('.form-input.error').forEach(input => {
            input.classList.remove('error');
        });
        form.querySelectorAll('.form-error').forEach(error => {
            error.remove();
        });
    },

    /**
     * Disable form inputs
     * @param {HTMLFormElement} form - Form element
     */
    disable(form) {
        form.querySelectorAll('input, button, select, textarea').forEach(el => {
            el.disabled = true;
        });
    },

    /**
     * Enable form inputs
     * @param {HTMLFormElement} form - Form element
     */
    enable(form) {
        form.querySelectorAll('input, button, select, textarea').forEach(el => {
            el.disabled = false;
        });
    },
};


// =============================================================================
// STORAGE HELPER
// =============================================================================

const Storage = {
    /**
     * Get item from localStorage
     * @param {string} key - Storage key
     * @param {*} defaultValue - Default value if not found
     * @returns {*} Stored value or default
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch {
            return defaultValue;
        }
    },

    /**
     * Set item in localStorage
     * @param {string} key - Storage key
     * @param {*} value - Value to store
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('localStorage not available:', e);
        }
    },

    /**
     * Remove item from localStorage
     * @param {string} key - Storage key
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('localStorage not available:', e);
        }
    },
};


// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Format file size for display
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @param {string} locale - Locale string
 * @returns {string} Formatted date
 */
function formatDate(date, locale = 'ar-DZ') {
    const d = new Date(date);
    return d.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

/**
 * Debounce function
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in ms
 * @returns {Function} Debounced function
 */
function debounce(fn, delay = 300) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}


// =============================================================================
// EXPORTS
// =============================================================================

window.API = API;
window.APIError = APIError;
window.Toast = Toast;
window.Loading = Loading;
window.Form = Form;
window.Storage = Storage;
window.formatFileSize = formatFileSize;
window.formatDate = formatDate;
window.debounce = debounce;
window.generateId = generateId;
