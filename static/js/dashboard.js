/**
 * Dashboard Overview Page JavaScript
 * Main dashboard with stats and quick actions
 */

const dashboard = {
    /**
     * Initialize the dashboard
     */
    init: function() {
        // Dashboard-specific initialization
        this.loadRecentActivity();
    },

    /**
     * Load recent activity or additional dashboard data
     */
    loadRecentActivity: async function() {
        // This could load recent imports, popular dreams, etc.
        // For now, we'll just ensure stats are loaded (handled by common.js)
        console.log('Dashboard initialized');
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    dashboard.init();
});