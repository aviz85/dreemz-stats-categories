/**
 * React Data Fix for PostgreSQL Compatibility
 * This script intercepts API responses and transforms them to be compatible with the React app
 */

(function() {
    // Store original fetch
    const originalFetch = window.fetch;
    
    /**
     * Transform PostgreSQL data to match expected React format
     */
    function transformData(data) {
        // If data is not an object, return as-is
        if (!data || typeof data !== 'object') return data;
        
        // Transform dreams array - ensure it's always an array
        if (data.dreams !== undefined) {
            if (!Array.isArray(data.dreams)) {
                console.warn('Dreams data is not an array, converting:', data.dreams);
                data.dreams = [];
            } else {
                // Ensure each dream object has proper numeric types
                data.dreams = data.dreams.map(dream => ({
                    ...dream,
                    count: Number(dream.count) || 0,
                    avg_age: dream.avg_age ? Number(dream.avg_age) : null,
                    min_age: dream.min_age ? Number(dream.min_age) : null,
                    max_age: dream.max_age ? Number(dream.max_age) : null
                }));
            }
        }
        
        // Transform categories array
        if (data.categories !== undefined) {
            if (!Array.isArray(data.categories)) {
                console.warn('Categories data is not an array, converting:', data.categories);
                data.categories = [];
            } else {
                data.categories = data.categories.map(cat => ({
                    ...cat,
                    count: Number(cat.count) || 0,
                    avg_age: cat.avg_age ? Number(cat.avg_age) : null,
                    min_age: cat.min_age ? Number(cat.min_age) : null,
                    max_age: cat.max_age ? Number(cat.max_age) : null,
                    dream_count: cat.dream_count ? Number(cat.dream_count) : null
                }));
            }
        }
        
        // Transform database stats
        if (data.database) {
            data.database = {
                ...data.database,
                total_dreams: Number(data.database.total_dreams) || 0,
                unique_titles: Number(data.database.unique_titles) || 0,
                categories: Number(data.database.categories) || 0,
                subcategories: Number(data.database.subcategories) || 0
            };
        }
        
        // Transform titles array
        if (data.titles !== undefined) {
            if (!Array.isArray(data.titles)) {
                console.warn('Titles data is not an array, converting:', data.titles);
                data.titles = [];
            } else {
                data.titles = data.titles.map(title => ({
                    ...title,
                    count: Number(title.count) || 0
                }));
            }
        }
        
        // Ensure total_count is a number
        if (data.total_count !== undefined) {
            data.total_count = Number(data.total_count) || 0;
        }
        
        // Ensure pagination values are numbers
        if (data.page !== undefined) {
            data.page = Number(data.page) || 0;
        }
        if (data.per_page !== undefined) {
            data.per_page = Number(data.per_page) || 50;
        }
        
        return data;
    }
    
    /**
     * Override fetch to intercept and transform API responses
     */
    window.fetch = function(...args) {
        return originalFetch.apply(this, args)
            .then(response => {
                // Store the original json method
                const originalJson = response.json.bind(response);
                
                // Override json method to transform data
                response.json = function() {
                    return originalJson().then(data => {
                        // Only transform API responses
                        const url = args[0];
                        if (typeof url === 'string' && url.includes('/api/')) {
                            console.log('Transforming API response for:', url);
                            return transformData(data);
                        }
                        return data;
                    });
                };
                
                return response;
            });
    };
    
    /**
     * Polyfill for Array methods in case they're missing
     */
    if (!Array.prototype.slice) {
        console.error('Array.slice is missing! Adding polyfill...');
        Array.prototype.slice = function(start, end) {
            const result = [];
            const len = this.length;
            start = start || 0;
            end = end === undefined ? len : end;
            
            for (let i = start; i < end && i < len; i++) {
                result.push(this[i]);
            }
            return result;
        };
    }
    
    /**
     * Fix for potential data type issues with Material-UI
     */
    window.addEventListener('error', function(e) {
        if (e.message && e.message.includes('.slice is not a function')) {
            console.error('Slice error caught:', e);
            console.log('This usually means data is not in array format');
            
            // Try to prevent the error from breaking the app
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);
    
    console.log('React PostgreSQL compatibility fix loaded successfully');
})();