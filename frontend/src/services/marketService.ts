import { apiClient } from './api';
import { MarketQuote, SecurityDetails } from '../types/market';

export const marketService = {
  async getBulkQuotes(symbols: string[]): Promise<Record<string, MarketQuote>> {
    const res = await apiClient.post<any>('/market/quotes', { symbols });
    // Support both direct dictionary { EFERT: {...} } and wrapped { quotes: { EFERT: {...} } }
    if (res.data && res.data.quotes && typeof res.data.quotes === 'object') {
      return res.data.quotes;
    }
    if (res.data && typeof res.data === 'object') {
      return res.data;
    }
    return {};
  },

  async getQuote(symbol: string): Promise<MarketQuote> {
    const res = await apiClient.get<MarketQuote>(`/market/quote/${symbol}`);
    return res.data;
  },

  async getSecurityDetails(symbol: string): Promise<SecurityDetails> {
    const res = await apiClient.get<SecurityDetails>(`/market/details/${symbol}`);
    return res.data;
  },
};