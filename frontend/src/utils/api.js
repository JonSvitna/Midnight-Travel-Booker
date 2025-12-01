import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          
          localStorage.setItem('access_token', response.data.access_token);
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

// Auth endpoints
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// User endpoints
export const userAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (data) => api.put('/users/profile', data),
  saveCredentials: (data) => api.post('/users/credentials', data),
  checkCredentials: () => api.get('/users/credentials'),
  deleteCredentials: () => api.delete('/users/credentials'),
};

// Booking endpoints
export const bookingAPI = {
  getAll: () => api.get('/bookings'),
  getOne: (id) => api.get(`/bookings/${id}`),
  create: (data) => api.post('/bookings', data),
  update: (id, data) => api.put(`/bookings/${id}`, data),
  cancel: (id) => api.delete(`/bookings/${id}`),
};

// Subscription endpoints
export const subscriptionAPI = {
  getCurrent: () => api.get('/subscriptions'),
  createCheckoutSession: (data) => api.post('/subscriptions/create-checkout-session', data),
};

// Admin endpoints
export const adminAPI = {
  getUsers: (page = 1, perPage = 20) => api.get(`/admin/users?page=${page}&per_page=${perPage}`),
  getUser: (id) => api.get(`/admin/users/${id}`),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  getBookings: (page = 1, perPage = 20, status = null) => {
    let url = `/admin/bookings?page=${page}&per_page=${perPage}`;
    if (status) url += `&status=${status}`;
    return api.get(url);
  },
  getAuditLogs: (page = 1, perPage = 50) => api.get(`/admin/audit-logs?page=${page}&per_page=${perPage}`),
  getStats: () => api.get('/admin/stats'),
};
