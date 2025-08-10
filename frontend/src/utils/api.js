import axios from 'axios';

const API_BASE = '/api';

// Get credentials from localStorage or prompt user
const getAuthCredentials = () => {
  let auth = localStorage.getItem('auth');
  if (!auth) {
    const username = prompt('Enter username:');
    const password = prompt('Enter password:');
    if (username && password) {
      auth = btoa(`${username}:${password}`);
      localStorage.setItem('auth', auth);
    }
  }
  return auth;
};

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Add authentication header to all requests
api.interceptors.request.use((config) => {
  const auth = getAuthCredentials();
  if (auth) {
    config.headers.Authorization = `Basic ${auth}`;
  }
  return config;
});

// Handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear stored credentials and retry
      localStorage.removeItem('auth');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const dashboardApi = {
  // Existing dashboard APIs
  getStatus: () => api.get('/status'),
  startPipeline: () => api.post('/start'),
  stopPipeline: () => api.post('/stop'),

  // New unique dreams APIs
  getUniqueDreams: (params = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.search) queryParams.append('search', params.search);
    if (params.age_from !== undefined) queryParams.append('age_from', params.age_from);
    if (params.age_to !== undefined) queryParams.append('age_to', params.age_to);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.offset) queryParams.append('offset', params.offset);
    if (params.sort) queryParams.append('sort', params.sort);
    if (params.order) queryParams.append('order', params.order);
    
    return api.get(`/unique-dreams?${queryParams.toString()}`);
  },

  getDreamDetails: (normalizedTitle) => 
    api.get(`/dream-details/${encodeURIComponent(normalizedTitle)}`),
};

export default api;