import { apiClient } from './api';
import { MarketQuote, SecurityDetails } from '../types/market';

export interface HistoricalPriceBar {
  trade_date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
}

export const marketService = {
  async getBulkQuotes(symbols: string[]): Promise<Record<string, MarketQuote>> {
    const res = await apiClient.post<any>('/market/quotes', { symbols });
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

  async getHistoricalPrices(symbol: string, days: number): Promise<HistoricalPriceBar[]> {
    const res = await apiClient.get<{ symbol: string; history: HistoricalPriceBar[] }>(
      `/market/historical/${symbol}?days=${days}`
    );
    return res.data.history || [];
  },
};