import { apiClient } from './api';
import { DividendAnalyticsData } from '../types/dividend';

export const dividendService = {
  async getDividendAnalytics(
    portfolioId: string = 'consolidated',
    year: string = 'all'
  ): Promise<DividendAnalyticsData> {
    const params = new URLSearchParams();
    if (portfolioId && portfolioId !== 'consolidated') {
      params.append('portfolio_id', portfolioId);
    }
    if (year && year !== 'all') {
      params.append('year', year);
    }

    const res = await apiClient.get<DividendAnalyticsData>(`/dividends/analytics?${params.toString()}`);
    return res.data;
  },
};