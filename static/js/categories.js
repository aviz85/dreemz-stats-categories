/**
 * Categories Analysis Page JavaScript
 * Handles categories analysis with age filtering
 */

const categoriesAnalysis = {
    /**
     * Initialize the categories analysis page
     */
    init: function() {
        this.setupEventListeners();
        this.load(); // Auto-load with default values
    },

    /**
     * Setup event listeners
     */
    setupEventListeners: function() {
        const { utils } = window.dreamAnalytics;
        
        // Auto-load when age values change
        const ageFrom = document.getElementById('ageFrom');
        const ageTo = document.getElementById('ageTo');
        
        if (ageFrom) {
            ageFrom.addEventListener('change', utils.debounce(() => this.load(), 300));
        }
        
        if (ageTo) {
            ageTo.addEventListener('change', utils.debounce(() => this.load(), 300));
        }

        // Enter key support
        [ageFrom, ageTo].forEach(input => {
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.load();
                    }
                });
            }
        });
    },

    /**
     * Load categories with current age filters
     */
    load: async function() {
        const { api, utils } = window.dreamAnalytics;

        try {
            // Get filter values
            const ageFrom = document.getElementById('ageFrom').value || 3;
            const ageTo = document.getElementById('ageTo').value || 125;

            // Build API parameters
            const params = {
                min_age: ageFrom,
                max_age: ageTo
            };

            // Show filters
            this.showFilters({
                ageRange: `${ageFrom}-${ageTo} years`
            });

            // Show loading state
            const tbody = document.getElementById('categoriesBody');
            utils.showLoading(tbody, 'Loading categories...');

            // Make API call
            const data = await api.getCategories(params);
            
            this.displayCategories(data.categories || []);

        } catch (error) {
            console.error('Error loading categories:', error);
            utils.showError('Failed to load categories data: ' + error.message);
        }
    },

    /**
     * Display categories in table
     */
    displayCategories: function(categories) {
        const { utils } = window.dreamAnalytics;
        const tbody = document.getElementById('categoriesBody');
        
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!categories || categories.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #666;">No categories found</td></tr>';
            return;
        }

        categories.forEach(cat => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="font-weight: 500;">${utils.escapeHtml(cat.category || '')}</td>
                <td><strong>${utils.formatNumber(cat.count)}</strong></td>
                <td>${cat.avg_age ? cat.avg_age.toFixed(1) : '-'}</td>
                <td>${cat.min_age || '-'} - ${cat.max_age || '-'}</td>
                <td><span style="background: #e3f2fd; padding: 3px 8px; border-radius: 12px; font-size: 12px;">${cat.top_age_group || '-'}</span></td>
                <td>
                    <button onclick="categoriesAnalysis.viewCategoryDreams('${utils.escapeHtml(cat.category)}')" 
                            style="font-size: 12px; padding: 5px 10px;">View Dreams</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    /**
     * Show filter summary
     */
    showFilters: function(filters) {
        const container = document.getElementById('categoryFilters');
        if (!container) return;

        const filterText = Object.entries(filters)
            .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
            .join(' | ');

        container.innerHTML = filterText;
        container.style.display = 'block';
    },

    /**
     * View dreams for specific category
     */
    viewCategoryDreams: async function(category) {
        const { api, utils } = window.dreamAnalytics;
        
        try {
            // Get dreams for this category
            const data = await api.getCategoryDreams(category, 'categories');
            
            // Navigate to dreams page with category filter
            const encodedCategory = encodeURIComponent(category);
            window.location.href = `/dreams?category=${encodedCategory}&type=categories`;
            
        } catch (error) {
            console.error('Error loading category dreams:', error);
            utils.showError('Failed to load category dreams: ' + error.message);
        }
    },

    /**
     * Clear filters and reload
     */
    clearFilters: function() {
        document.getElementById('ageFrom').value = '13';
        document.getElementById('ageTo').value = '60';
        document.getElementById('categoryFilters').style.display = 'none';
        this.load();
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    categoriesAnalysis.init();
});