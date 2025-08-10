/**
 * Dream Details Explorer Page JavaScript
 * Handles detailed dream information and title browsing
 */

const dreamExplorer = {
    allTitles: [],

    /**
     * Initialize the dream explorer page
     */
    init: function() {
        this.setupEventListeners();
        this.checkUrlParams();
        this.loadAllTitles();
    },

    /**
     * Setup event listeners
     */
    setupEventListeners: function() {
        const dreamTitleInput = document.getElementById('dreamTitleInput');
        if (dreamTitleInput) {
            dreamTitleInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.explore();
                }
            });
        }

        const titleSearchInput = document.getElementById('titleSearchInput');
        if (titleSearchInput) {
            const { utils } = window.dreamAnalytics;
            titleSearchInput.addEventListener('input', 
                utils.debounce(() => this.filterTitles(), 200)
            );
        }
    },

    /**
     * Check URL parameters for auto-loading dream
     */
    checkUrlParams: function() {
        const urlParams = new URLSearchParams(window.location.search);
        const title = urlParams.get('title');
        
        if (title) {
            document.getElementById('dreamTitleInput').value = decodeURIComponent(title);
            this.explore();
        }
    },

    /**
     * Load all available dream titles for browsing
     */
    loadAllTitles: async function() {
        const { api } = window.dreamAnalytics;
        
        try {
            const data = await api.getAllTitles();
            this.allTitles = data.titles || [];
        } catch (error) {
            console.error('Error loading titles:', error);
        }
    },

    /**
     * Explore specific dream details
     */
    explore: async function() {
        const { api, utils } = window.dreamAnalytics;
        
        const dreamTitle = document.getElementById('dreamTitleInput').value.trim();
        if (!dreamTitle) {
            utils.showError('Please enter a dream title to explore');
            return;
        }

        try {
            const container = document.getElementById('dreamDetailsContent');
            utils.showLoading(container, 'Loading dream details...');

            const data = await api.getDreamDetails(dreamTitle);
            this.displayDreamDetails(data);

        } catch (error) {
            console.error('Error loading dream details:', error);
            utils.showError('Failed to load dream details: ' + error.message);
        }
    },

    /**
     * Display dream details
     */
    displayDreamDetails: function(data) {
        const { utils } = window.dreamAnalytics;
        const container = document.getElementById('dreamDetailsContent');
        
        if (!data.dreams || data.dreams.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No details found for this dream title.</p>';
            return;
        }

        const dreams = data.dreams;
        const title = data.normalized_title;
        
        let html = `
            <div class="dream-details">
                <div class="dream-title">${utils.escapeHtml(title)}</div>
                <div class="dream-stats">
                    <span><strong>Total instances:</strong> ${dreams.length}</span>
                    <span><strong>Age range:</strong> ${Math.min(...dreams.map(d => d.age))} - ${Math.max(...dreams.map(d => d.age))} years</span>
                    <span><strong>Average age:</strong> ${(dreams.reduce((sum, d) => sum + d.age, 0) / dreams.length).toFixed(1)} years</span>
                </div>
            </div>
        `;

        // Age distribution
        const ageGroups = this.calculateAgeGroups(dreams);
        html += `
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-bottom: 15px; color: #333;">Age Distribution</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px;">
                    ${Object.entries(ageGroups).map(([group, count]) => `
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 5px;">
                            <div style="font-weight: bold; color: #667eea;">${count}</div>
                            <div style="font-size: 12px; color: #666;">${group}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Categories analysis
        const categories = this.extractCategories(dreams);
        if (categories.length > 0) {
            html += `
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-bottom: 15px; color: #333;">Most Common Categories</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${categories.slice(0, 10).map(cat => `
                            <span style="background: #667eea; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">
                                ${utils.escapeHtml(cat.name)} (${cat.count})
                            </span>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Detailed instances table
        html += `
            <div class="table-container" style="margin-top: 20px;">
                <table>
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Age</th>
                            <th>Categories</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        dreams.forEach(dream => {
            const categories = dream.categories ? dream.categories
                .filter(cat => cat && cat.category)
                .map(cat => `${cat.category}${cat.subcategory ? ' → ' + cat.subcategory : ''}`)
                .join('<br>') : 'No categories';

            html += `
                <tr>
                    <td>${utils.escapeHtml(dream.username || 'Anonymous')}</td>
                    <td>${dream.age || '-'}</td>
                    <td style="font-size: 12px;">${categories}</td>
                </tr>
            `;
        });

        html += '</tbody></table></div>';
        container.innerHTML = html;
    },

    /**
     * Calculate age group distribution
     */
    calculateAgeGroups: function(dreams) {
        const groups = {
            'Under 13': 0,
            '13-18': 0,
            '19-30': 0,
            '31-45': 0,
            '46-60': 0,
            '60+': 0
        };

        dreams.forEach(dream => {
            const age = dream.age;
            if (age < 13) groups['Under 13']++;
            else if (age <= 18) groups['13-18']++;
            else if (age <= 30) groups['19-30']++;
            else if (age <= 45) groups['31-45']++;
            else if (age <= 60) groups['46-60']++;
            else groups['60+']++;
        });

        return groups;
    },

    /**
     * Extract and count categories
     */
    extractCategories: function(dreams) {
        const categoryCount = {};

        dreams.forEach(dream => {
            if (dream.categories) {
                dream.categories.forEach(cat => {
                    if (cat && cat.category) {
                        const name = cat.subcategory 
                            ? `${cat.category} → ${cat.subcategory}`
                            : cat.category;
                        categoryCount[name] = (categoryCount[name] || 0) + 1;
                    }
                });
            }
        });

        return Object.entries(categoryCount)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count);
    },

    /**
     * Show title browser modal
     */
    showTitleBrowser: function() {
        const modal = document.getElementById('titleBrowserModal');
        if (modal) {
            modal.style.display = 'block';
            this.displayTitles(this.allTitles);
        }
    },

    /**
     * Close title browser modal
     */
    closeTitleBrowser: function() {
        const modal = document.getElementById('titleBrowserModal');
        if (modal) {
            modal.style.display = 'none';
        }
    },

    /**
     * Filter titles based on search
     */
    filterTitles: function() {
        const search = document.getElementById('titleSearchInput').value.toLowerCase();
        const filtered = this.allTitles.filter(title => 
            title.title.toLowerCase().includes(search)
        );
        this.displayTitles(filtered.slice(0, 100)); // Limit to 100 for performance
    },

    /**
     * Display titles in the browser
     */
    displayTitles: function(titles) {
        const { utils } = window.dreamAnalytics;
        const container = document.getElementById('titlesList');
        
        if (!titles || titles.length === 0) {
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">No titles found</div>';
            return;
        }

        container.innerHTML = titles.map(title => `
            <div style="padding: 10px; border-bottom: 1px solid #e1e5e9; cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
                 onclick="dreamExplorer.selectTitle('${utils.escapeHtml(title.title)}')">
                <span style="font-weight: 500;">${utils.escapeHtml(title.title)}</span>
                <span style="color: #666; font-size: 12px;">${title.count} instances</span>
            </div>
        `).join('');
    },

    /**
     * Select a title from the browser
     */
    selectTitle: function(title) {
        document.getElementById('dreamTitleInput').value = title;
        this.closeTitleBrowser();
        this.explore();
    },

    /**
     * Clear the explorer
     */
    clear: function() {
        document.getElementById('dreamTitleInput').value = '';
        document.getElementById('dreamDetailsContent').innerHTML = `
            <p style="text-align: center; color: #666; padding: 40px;">
                Enter a dream title above to see detailed information about that specific dream.
            </p>
        `;
        
        // Update URL
        window.history.pushState({}, '', '/dream-details');
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    dreamExplorer.init();
});