import { apiClient } from './api';
import { AuthResponse, User } from '../types/auth';

export const authService = {
  async register(email: string, password: string, full_name: string): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/register', { email, password, full_name });
    return res.data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/login', { email, password });
    return res.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Continue client cleanup even if network fails
    }
  },

  async getMe(): Promise<{ user: User }> {
    const res = await apiClient.get<{ user: User }>('/auth/me');
    return res.data;
  },
};