/**
 * Elder - Main JavaScript file
 * Handles API calls, authentication, and common UI interactions
 */

// API Base URL
const API_BASE = '/api/v1';

// Configure axios defaults
axios.defaults.baseURL = API_BASE;
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add authentication token to all requests
axios.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// Handle token expiration
axios.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        // If 401 and not already retrying, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post(`${API_BASE}/auth/refresh`, {
                        refresh_token: refreshToken
                    });

                    if (response.data.access_token) {
                        localStorage.setItem('access_token', response.data.access_token);
                        originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
                        return axios(originalRequest);
                    }
                } catch (refreshError) {
                    // Refresh failed, redirect to login
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                }
            } else {
                // No refresh token, redirect to login
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

/**
 * Show alert message
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    if (duration > 0) {
        setTimeout(() => alertDiv.remove(), duration);
    }
}

/**
 * Show loading spinner
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Format date (date only)
 */
function formatDateOnly(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        showAlert('Failed to copy to clipboard', 'danger', 3000);
    }
}

/**
 * Confirm action with modal or native dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Initialize theme toggle (if implemented)
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', currentTheme);

        themeToggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = theme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * API Helper Functions
 */
const API = {
    // Organizations
    organizations: {
        list: (params = {}) => axios.get('/organizations', { params }),
        get: (id) => axios.get(`/organizations/${id}`),
        create: (data) => axios.post('/organizations', data),
        update: (id, data) => axios.patch(`/organizations/${id}`, data),
        delete: (id) => axios.delete(`/organizations/${id}`)
    },

    // Entities
    entities: {
        list: (params = {}) => axios.get('/entities', { params }),
        get: (id) => axios.get(`/entities/${id}`),
        create: (data) => axios.post('/entities', data),
        update: (id, data) => axios.patch(`/entities/${id}`, data),
        delete: (id) => axios.delete(`/entities/${id}`)
    },

    // Dependencies
    dependencies: {
        list: (params = {}) => axios.get('/dependencies', { params }),
        create: (data) => axios.post('/dependencies', data),
        delete: (id) => axios.delete(`/dependencies/${id}`)
    },

    // Graph
    graph: {
        get: (params = {}) => axios.get('/graph', { params }),
        analyze: (params = {}) => axios.get('/graph/analyze', { params })
    },

    // Issues (Enterprise)
    issues: {
        list: (params = {}) => axios.get('/issues', { params }),
        get: (id) => axios.get(`/issues/${id}`),
        create: (data) => axios.post('/issues', data),
        update: (id, data) => axios.patch(`/issues/${id}`, data),
        delete: (id) => axios.delete(`/issues/${id}`)
    },

    // Metadata (Enterprise)
    metadata: {
        getEntity: (entityId) => axios.get(`/metadata/entities/${entityId}/metadata`),
        setEntity: (entityId, data) => axios.post(`/metadata/entities/${entityId}/metadata`, data),
        updateEntity: (entityId, fieldKey, data) => axios.patch(`/metadata/entities/${entityId}/metadata/${fieldKey}`, data),
        deleteEntity: (entityId, fieldKey) => axios.delete(`/metadata/entities/${entityId}/metadata/${fieldKey}`)
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initTooltips();
    initPopovers();
});

// Export for use in other scripts
window.ElderAPI = API;
window.showAlert = showAlert;
window.showLoading = showLoading;
window.formatDate = formatDate;
window.formatDateOnly = formatDateOnly;
window.copyToClipboard = copyToClipboard;
window.confirmAction = confirmAction;
