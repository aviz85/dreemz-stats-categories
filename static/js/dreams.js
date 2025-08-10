/**
 * Dreams Analysis Page JavaScript
 * Handles unique dreams search, filtering, and pagination
 */

const dreamsAnalysis = {
    // State management
    currentOffset: 0,
    currentLimit: 50,
    currentFilters: {},
    totalCount: 0,

    /**
     * Initialize the dreams analysis page
     */
    init: function() {
        this.setupEventListeners();
        this.search();
    },

    /**
     * Setup event listeners for search inputs
     */
    setupEventListeners: function() {
        const { utils } = window.dreamAnalytics;
        
        // Debounced search on input
        const debouncedSearch = utils.debounce(() => this.search(), 300);
        
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', debouncedSearch);
        }

        const ageFrom = document.getElementById('ageFrom');
        if (ageFrom) {
            ageFrom.addEventListener('change', debouncedSearch);
        }

        const ageTo = document.getElementById('ageTo');
        if (ageTo) {
            ageTo.addEventListener('change', debouncedSearch);
        }

        const sortBy = document.getElementById('sortBy');
        if (sortBy) {
            sortBy.addEventListener('change', debouncedSearch);
        }

        const limitSelect = document.getElementById('limitSelect');
        if (limitSelect) {
            limitSelect.addEventListener('change', debouncedSearch);
        }

        // Enter key support
        [searchInput, ageFrom, ageTo].forEach(input => {
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.search();
                    }
                });
            }
        });
    },

    /**
     * Perform dreams search with current filters
     */
    search: async function() {
        this.currentOffset = 0;
        await this.loadDreams();
    },

    /**
     * Load dreams with current settings
     */
    loadDreams: async function() {
        const { api, utils } = window.dreamAnalytics;

        try {
            // Get filter values
            const search = document.getElementById('searchInput').value;
            const ageFrom = document.getElementById('ageFrom').value;
            const ageTo = document.getElementById('ageTo').value;
            const sortBy = document.getElementById('sortBy').value;
            const limitValue = document.getElementById('limitSelect').value;
            
            this.currentLimit = limitValue === '-1' ? 10000 : parseInt(limitValue);
            this.currentFilters = { search, ageFrom, ageTo, sortBy, limit: this.currentLimit };

            // Build API parameters
            const params = {
                limit: this.currentLimit,
                offset: this.currentOffset,
                sort: sortBy,
                order: 'desc'
            };

            if (search) params.search = search;
            if (ageFrom) params.age_from = ageFrom;
            if (ageTo) params.age_to = ageTo;

            // Show filters
            this.showFilters({
                search: search || 'All dreams',
                ageRange: (ageFrom || ageTo) ? `${ageFrom || 'any'}-${ageTo || 'any'} years` : 'All ages',
                sortBy: sortBy,
                limit: limitValue === '-1' ? 'All results (Long Tail)' : `Top ${limitValue}`
            });

            // Show loading state
            const tbody = document.getElementById('dreamsBody');
            utils.showLoading(tbody, 'Loading dreams...');

            // Make API call
            const data = await api.getUniqueDreams(params);
            
            this.totalCount = data.total_count || 0;
            this.displayDreams(data.dreams || []);
            this.updatePagination();

        } catch (error) {
            console.error('Error loading dreams:', error);
            utils.showError('Failed to load dreams data: ' + error.message);
        }
    },

    /**
     * Display dreams in table
     */
    displayDreams: function(dreams) {
        const { utils } = window.dreamAnalytics;
        const tbody = document.getElementById('dreamsBody');
        
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!dreams || dreams.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #666;">No dreams found</td></tr>';
            return;
        }

        dreams.forEach(dream => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="font-weight: 500;">${utils.escapeHtml(dream.normalized_title || '')}</td>
                <td><strong>${utils.formatNumber(dream.count)}</strong></td>
                <td>${dream.avg_age ? dream.avg_age.toFixed(1) : '-'}</td>
                <td>${dream.min_age || '-'} - ${dream.max_age || '-'}</td>
                <td>
                    <button onclick="dreamsAnalysis.exploreDream('${utils.escapeHtml(dream.normalized_title)}')" 
                            style="font-size: 12px; padding: 5px 10px;">Explore</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    /**
     * Show filter summary
     */
    showFilters: function(filters) {
        const container = document.getElementById('dreamFilters');
        if (!container) return;

        const filterText = Object.entries(filters)
            .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
            .join(' | ');

        container.innerHTML = filterText;
        container.style.display = 'block';
    },

    /**
     * Navigate to next page
     */
    nextPage: async function() {
        if (this.currentOffset + this.currentLimit < this.totalCount) {
            this.currentOffset += this.currentLimit;
            await this.loadDreams();
        }
    },

    /**
     * Navigate to previous page
     */
    previousPage: async function() {
        if (this.currentOffset > 0) {
            this.currentOffset = Math.max(0, this.currentOffset - this.currentLimit);
            await this.loadDreams();
        }
    },

    /**
     * Update pagination controls
     */
    updatePagination: function() {
        const currentPage = Math.floor(this.currentOffset / this.currentLimit) + 1;
        const totalPages = Math.ceil(this.totalCount / this.currentLimit);
        
        const pageInfo = document.getElementById('pageInfo');
        if (pageInfo) {
            pageInfo.textContent = `Page ${currentPage} of ${totalPages} (${this.totalCount.toLocaleString()} total)`;
        }
        
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentOffset === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentOffset + this.currentLimit >= this.totalCount;
        }
    },

    /**
     * Clear all filters
     */
    clearFilters: function() {
        document.getElementById('searchInput').value = '';
        document.getElementById('ageFrom').value = '';
        document.getElementById('ageTo').value = '';
        document.getElementById('sortBy').value = 'count';
        document.getElementById('limitSelect').value = '50';
        document.getElementById('dreamFilters').style.display = 'none';
        this.search();
    },

    /**
     * Navigate to dream details page for specific dream
     */
    exploreDream: function(title) {
        const encodedTitle = encodeURIComponent(title);
        window.location.href = `/dream-details?title=${encodedTitle}`;
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    dreamsAnalysis.init();
});