import { apiClient } from './api';
import { MarketQuote, Security } from '../types/market';

export const marketService = {
  async getSymbols(query?: string, sector?: string): Promise<Security[]> {
    const res = await apiClient.get<{ count: number; securities: Security[] }>('/market/symbols', {
      params: { query, sector },
    });
    return res.data.securities;
  },

  async getQuote(symbol: string): Promise<MarketQuote> {
    const res = await apiClient.get<MarketQuote>(`/market/quote/${symbol}`);
    return res.data;
  },

  async getBulkQuotes(symbols: string[]): Promise<Record<string, MarketQuote>> {
    const res = await apiClient.post<{ quotes: Record<string, MarketQuote> }>('/market/quotes', { symbols });
    return res.data.quotes;
  },
};