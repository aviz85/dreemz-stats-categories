import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

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