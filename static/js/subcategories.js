/**
 * Subcategories Analysis Page JavaScript
 * Handles subcategories analysis with age filtering and search
 */

const subcategoriesAnalysis = {
    /**
     * Initialize the subcategories analysis page
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
        
        // Auto-load when values change
        const ageFrom = document.getElementById('ageFrom');
        const ageTo = document.getElementById('ageTo');
        const searchInput = document.getElementById('searchInput');
        
        const debouncedLoad = utils.debounce(() => this.load(), 300);
        
        if (ageFrom) {
            ageFrom.addEventListener('change', debouncedLoad);
        }
        
        if (ageTo) {
            ageTo.addEventListener('change', debouncedLoad);
        }

        if (searchInput) {
            searchInput.addEventListener('input', debouncedLoad);
        }

        // Enter key support
        [ageFrom, ageTo, searchInput].forEach(input => {
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
     * Load subcategories with current filters
     */
    load: async function() {
        const { api, utils } = window.dreamAnalytics;

        try {
            // Get filter values
            const ageFrom = document.getElementById('ageFrom').value || 3;
            const ageTo = document.getElementById('ageTo').value || 125;
            const search = document.getElementById('searchInput').value;

            // Build API parameters
            const params = {
                min_age: ageFrom,
                max_age: ageTo
            };

            // Show filters
            this.showFilters({
                ageRange: `${ageFrom}-${ageTo} years`,
                search: search || 'All subcategories'
            });

            // Show loading state
            const tbody = document.getElementById('subcategoriesBody');
            utils.showLoading(tbody, 'Loading subcategories...');

            // Make API call
            const data = await api.getSubcategories(params);
            
            let subcategories = data.categories || [];
            
            // Filter by search term if provided
            if (search) {
                subcategories = subcategories.filter(sub => 
                    sub.category && sub.category.toLowerCase().includes(search.toLowerCase())
                );
            }

            this.displaySubcategories(subcategories);

        } catch (error) {
            console.error('Error loading subcategories:', error);
            utils.showError('Failed to load subcategories data: ' + error.message);
        }
    },

    /**
     * Display subcategories in table
     */
    displaySubcategories: function(subcategories) {
        const { utils } = window.dreamAnalytics;
        const tbody = document.getElementById('subcategoriesBody');
        
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!subcategories || subcategories.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #666;">No subcategories found</td></tr>';
            return;
        }

        subcategories.forEach(sub => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="font-weight: 500;">${utils.escapeHtml(sub.category || '')}</td>
                <td><strong>${utils.formatNumber(sub.count)}</strong></td>
                <td>${sub.avg_age ? sub.avg_age.toFixed(1) : '-'}</td>
                <td>${sub.min_age || '-'} - ${sub.max_age || '-'}</td>
                <td><span style="background: #e8f5e9; padding: 3px 8px; border-radius: 12px; font-size: 12px;">${sub.top_age_group || '-'}</span></td>
                <td>
                    <button onclick="subcategoriesAnalysis.viewCategoryDreams('${utils.escapeHtml(sub.category)}')" 
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
        const container = document.getElementById('subcategoryFilters');
        if (!container) return;

        const filterText = Object.entries(filters)
            .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
            .join(' | ');

        container.innerHTML = filterText;
        container.style.display = 'block';
    },

    /**
     * View dreams for specific subcategory
     */
    viewCategoryDreams: async function(category) {
        const { api, utils } = window.dreamAnalytics;
        
        try {
            // Get dreams for this subcategory
            const data = await api.getCategoryDreams(category, 'subcategories');
            
            // Navigate to dreams page with category filter
            const encodedCategory = encodeURIComponent(category);
            window.location.href = `/dreams?category=${encodedCategory}&type=subcategories`;
            
        } catch (error) {
            console.error('Error loading subcategory dreams:', error);
            utils.showError('Failed to load subcategory dreams: ' + error.message);
        }
    },

    /**
     * Clear filters and reload
     */
    clearFilters: function() {
        document.getElementById('ageFrom').value = '18';
        document.getElementById('ageTo').value = '25';
        document.getElementById('searchInput').value = '';
        document.getElementById('subcategoryFilters').style.display = 'none';
        this.load();
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    subcategoriesAnalysis.init();
});