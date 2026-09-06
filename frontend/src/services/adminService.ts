import { apiClient } from './api';

export interface AdminUserItem {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  is_active: boolean;
  portfolio_count: number;
  created_at: string;
}

export interface AdminUserListResponse {
  users: AdminUserItem[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export const adminService = {
  async listUsers(page = 1, search?: string): Promise<AdminUserListResponse> {
    const params: Record<string, any> = { page, per_page: 20 };
    if (search) params.search = search;
    const res = await apiClient.get<AdminUserListResponse>('/admin/users', { params });
    return res.data;
  },

  async resetPassword(userId: string, newPassword: string): Promise<void> {
    await apiClient.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword });
  },

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/admin/users/${userId}`);
  },
};