/**
 * API utilities for Dream Analytics Dashboard
 * Handles all API calls with proper error handling and data transformation
 */

// API configuration
const API_BASE = '';

/**
 * Generic API request handler with error handling
 */
export const apiRequest = async (endpoint, options = {}) => {
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
};

/**
 * Transform database row data to ensure proper types
 * Fixes issues with PostgreSQL data types vs SQLite
 */
export const transformRowData = (data) => {
  if (!data || typeof data !== 'object') return data;

  const transformed = {};
  
  Object.entries(data).forEach(([key, value]) => {
    // Handle null/undefined values
    if (value === null || value === undefined) {
      transformed[key] = value;
      return;
    }

    // Convert PostgreSQL Decimal types to numbers
    if (typeof value === 'object' && value.constructor && value.constructor.name === 'Decimal') {
      transformed[key] = parseFloat(value);
      return;
    }

    // Ensure age-related fields are numbers
    if (key.includes('age') || key === 'count') {
      const numValue = parseFloat(value);
      transformed[key] = isNaN(numValue) ? value : numValue;
      return;
    }

    // Handle array fields that might come as objects
    if (key === 'categories' && !Array.isArray(value)) {
      transformed[key] = [];
      return;
    }

    transformed[key] = value;
  });

  return transformed;
};

/**
 * Transform array of database rows
 */
export const transformArrayData = (data) => {
  if (!Array.isArray(data)) return data;
  return data.map(transformRowData);
};

/**
 * Build URL parameters safely
 */
export const buildParams = (params) => {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      urlParams.append(key, value);
    }
  });
  return urlParams;
};

/**
 * API endpoints
 */
export const api = {
  // Get database status and stats
  getStatus: async () => {
    const data = await apiRequest('/api/status');
    return {
      ...data,
      database: data.database ? transformRowData(data.database) : null
    };
  },

  // Get unique dreams with filters
  getUniqueDreams: async (params = {}) => {
    const urlParams = buildParams(params);
    const data = await apiRequest(`/api/unique-dreams?${urlParams}`);
    return {
      ...data,
      dreams: transformArrayData(data.dreams || [])
    };
  },

  // Get dream details for specific title
  getDreamDetails: async (title) => {
    const data = await apiRequest(`/api/dream-details/${encodeURIComponent(title)}`);
    return {
      ...data,
      dreams: transformArrayData(data.dreams || [])
    };
  },

  // Get categories analysis
  getCategories: async (params = {}) => {
    const urlParams = buildParams(params);
    const data = await apiRequest(`/api/categories-analysis?${urlParams}`);
    return {
      ...data,
      categories: transformArrayData(data.categories || [])
    };
  },

  // Get subcategories analysis
  getSubcategories: async (params = {}) => {
    const urlParams = buildParams(params);
    const data = await apiRequest(`/api/subcategories-analysis?${urlParams}`);
    return {
      ...data,
      categories: transformArrayData(data.categories || [])
    };
  },

  // Get dreams for specific category
  getCategoryDreams: async (category, type = 'categories') => {
    const params = buildParams({ category, type });
    const data = await apiRequest(`/api/category-dreams?${params}`);
    return {
      ...data,
      dreams: transformArrayData(data.dreams || [])
    };
  },

  // Get all dream titles
  getAllTitles: async () => {
    const data = await apiRequest('/api/all-titles');
    return {
      ...data,
      titles: transformArrayData(data.titles || [])
    };
  },

  // Import endpoints
  startImport: async (force = false) => {
    return await apiRequest('/api/import/start', {
      method: 'POST',
      body: JSON.stringify({ force })
    });
  },

  getImportStatus: async () => {
    return await apiRequest('/api/import/status');
  }
};