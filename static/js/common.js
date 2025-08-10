/**
 * Common utilities for Dream Analytics Dashboard
 * Shared functions across all dashboard pages
 */

// API Base URL
const API_BASE = '';

// Common utility functions
const utils = {
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Format numbers with thousand separators
     */
    formatNumber: function(num) {
        if (num === null || num === undefined) return '-';
        return num.toLocaleString();
    },

    /**
     * Show error message
     */
    showError: function(message) {
        this.removeMessage();
        const container = document.querySelector('.container');
        if (!container) return;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = message;
        container.insertBefore(errorDiv, container.firstChild);
        
        setTimeout(() => errorDiv.remove(), 8000);
    },

    /**
     * Show success message
     */
    showSuccess: function(message) {
        this.removeMessage();
        const container = document.querySelector('.container');
        if (!container) return;
        
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = message;
        container.insertBefore(successDiv, container.firstChild);
        
        setTimeout(() => successDiv.remove(), 5000);
    },

    /**
     * Remove existing messages
     */
    removeMessage: function() {
        const container = document.querySelector('.container');
        if (!container) return;
        
        const existing = container.querySelector('.error, .success');
        if (existing) existing.remove();
    },

    /**
     * Show loading state in element
     */
    showLoading: function(element, message = 'Loading...') {
        if (!element) return;
        element.innerHTML = `<div class="loading">${message}</div>`;
    },

    /**
     * Build URL search params safely
     */
    buildParams: function(params) {
        const urlParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                urlParams.append(key, value);
            }
        });
        return urlParams;
    },

    /**
     * Make API request with error handling
     */
    apiRequest: async function(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },

    /**
     * Set active navigation tab
     */
    setActiveNavTab: function(currentPath) {
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('href') === currentPath) {
                tab.classList.add('active');
            }
        });
    },

    /**
     * Debounce function calls
     */
    debounce: function(func, wait) {
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
};

// API endpoints wrapper
const api = {
    /**
     * Get database status and stats
     */
    getStatus: function() {
        return utils.apiRequest('/api/status');
    },

    /**
     * Get unique dreams with filters
     */
    getUniqueDreams: function(params = {}) {
        const urlParams = utils.buildParams(params);
        return utils.apiRequest(`/api/unique-dreams?${urlParams}`);
    },

    /**
     * Get dream details for specific title
     */
    getDreamDetails: function(title) {
        return utils.apiRequest(`/api/dream-details/${encodeURIComponent(title)}`);
    },

    /**
     * Get categories analysis
     */
    getCategories: function(params = {}) {
        const urlParams = utils.buildParams(params);
        return utils.apiRequest(`/api/categories-analysis?${urlParams}`);
    },

    /**
     * Get subcategories analysis
     */
    getSubcategories: function(params = {}) {
        const urlParams = utils.buildParams(params);
        return utils.apiRequest(`/api/subcategories-analysis?${urlParams}`);
    },

    /**
     * Get dreams for specific category
     */
    getCategoryDreams: function(category, type = 'categories') {
        const params = utils.buildParams({ category, type });
        return utils.apiRequest(`/api/category-dreams?${params}`);
    },

    /**
     * Get all dream titles
     */
    getAllTitles: function() {
        return utils.apiRequest('/api/all-titles');
    }
};

// Global stats loader - used across all pages
const statsLoader = {
    /**
     * Load and display stats in elements with IDs: totalDreams, uniqueTitles, categories, subcategories
     */
    load: async function() {
        try {
            const data = await api.getStatus();
            
            if (data.database) {
                const db = data.database;
                
                const elements = {
                    totalDreams: utils.formatNumber(db.total_dreams),
                    uniqueTitles: utils.formatNumber(db.unique_titles),
                    categories: utils.formatNumber(db.categories),
                    subcategories: utils.formatNumber(db.subcategories)
                };

                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) element.textContent = value;
                });

                // Update summary content if it exists
                this.updateSummary(db);
                
                return db;
            }
        } catch (error) {
            console.error('Error loading stats:', error);
            utils.showError('Failed to load database statistics');
        }
    },

    /**
     * Update summary content
     */
    updateSummary: function(db) {
        const summaryContent = document.getElementById('summaryContent');
        if (!summaryContent) return;

        const duplicateRate = db.total_dreams > 0 
            ? ((db.total_dreams - db.unique_titles) / db.total_dreams * 100).toFixed(1)
            : 0;

        const avgSubcatsPerCategory = db.categories > 0 
            ? Math.round(db.subcategories / db.categories) 
            : 0;

        summaryContent.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="color: #667eea; margin-bottom: 10px;">💾 Database Info</h3>
                    <p><strong>Total Dreams:</strong> ${utils.formatNumber(db.total_dreams)}</p>
                    <p><strong>Unique Titles:</strong> ${utils.formatNumber(db.unique_titles)}</p>
                    <p><strong>Duplicate Rate:</strong> ${duplicateRate}%</p>
                </div>
                <div>
                    <h3 style="color: #667eea; margin-bottom: 10px;">📊 Classification</h3>
                    <p><strong>Categories:</strong> ${utils.formatNumber(db.categories)}</p>
                    <p><strong>Subcategories:</strong> ${utils.formatNumber(db.subcategories)}</p>
                    <p><strong>Avg per Category:</strong> ${avgSubcatsPerCategory} subcategories</p>
                </div>
            </div>
        `;
    }
};

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set active nav tab based on current path
    utils.setActiveNavTab(window.location.pathname);
    
    // Load stats on all pages
    statsLoader.load();
});

// Export for other modules
window.dreamAnalytics = {
    utils,
    api,
    statsLoader
};