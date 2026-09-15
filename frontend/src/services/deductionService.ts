import { apiClient } from './api';
import { DeductionAnalyticsData } from '../types/deduction';

export const deductionService = {
  async getDeductionAnalytics(
    portfolioId: string = 'consolidated',
    year: string = 'all'
  ): Promise<DeductionAnalyticsData> {
    const params = new URLSearchParams();
    if (portfolioId && portfolioId !== 'consolidated') {
      params.append('portfolio_id', portfolioId);
    }
    if (year && year !== 'all') {
      params.append('year', year);
    }

    const res = await apiClient.get<DeductionAnalyticsData>(`/deductions/analytics?${params.toString()}`);
    return res.data;
  },
};