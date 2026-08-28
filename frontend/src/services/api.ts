import axios from 'axios';
import { AuthTokens } from '../types/auth';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization Bearer token to all outgoing requests
apiClient.interceptors.request.use((config) => {
  const storedTokens = localStorage.getItem('psx_auth_tokens');
  if (storedTokens) {
    try {
      const tokens: AuthTokens = JSON.parse(storedTokens);
      if (tokens.access_token) {
        config.headers.Authorization = `Bearer ${tokens.access_token}`;
      }
    } catch {
      // Ignore parse error
    }
  }
  return config;
});

// Intercept 401 Unauthorized responses to attempt token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const storedTokens = localStorage.getItem('psx_auth_tokens');
      if (storedTokens) {
        try {
          const tokens: AuthTokens = JSON.parse(storedTokens);
          if (tokens.refresh_token) {
            const refreshRes = await axios.post('/api/v1/auth/refresh', {
              refresh_token: tokens.refresh_token,
            });
            const newAccessToken = refreshRes.data.access_token;
            tokens.access_token = newAccessToken;
            localStorage.setItem('psx_auth_tokens', JSON.stringify(tokens));

            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return apiClient(originalRequest);
          }
        } catch {
          localStorage.removeItem('psx_auth_tokens');
          localStorage.removeItem('psx_auth_user');
          window.location.href = '/';
        }
      }
    }
    return Promise.reject(error);
  }
);