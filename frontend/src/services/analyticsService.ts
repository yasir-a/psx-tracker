import { apiClient } from './api';
import { AnalyticsResponse } from '../types/analytics';

export const analyticsService = {
  async getAnalyticsSummary(portfolioId?: string): Promise<AnalyticsResponse> {
    const res = await apiClient.get<AnalyticsResponse>('/analytics/summary', {
      params: { portfolio_id: portfolioId },
    });
    return res.data;
  },
};