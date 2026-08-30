import { apiClient } from './api';
import { PortfolioValuationResponse, TransactionRecord } from '../types/portfolio';

export interface PortfolioListItem {
  id: string;
  name: string;
  description?: string;
  is_default: boolean;
  cash_balance: number;
}

export const portfolioService = {
  async getMyPortfolios(): Promise<{ portfolios: PortfolioListItem[] }> {
    const res = await apiClient.get('/portfolio/mine');
    return res.data;
  },

  async createPortfolio(payload: { name: string; description?: string }): Promise<PortfolioListItem> {
    const res = await apiClient.post<PortfolioListItem>('/portfolio/create', payload);
    return res.data;
  },

  async deletePortfolio(portfolioId: string): Promise<void> {
    await apiClient.delete(`/portfolio/${portfolioId}`);
  },

  async getValuation(portfolioId: string): Promise<PortfolioValuationResponse> {
    if (portfolioId === 'consolidated') {
      const res = await apiClient.get<PortfolioValuationResponse>('/portfolio/consolidated-valuation');
      return res.data;
    }
    const res = await apiClient.get<PortfolioValuationResponse>(`/portfolio/${portfolioId}/valuation`);
    return res.data;
  },

  async getTransactions(portfolioId: string): Promise<TransactionRecord[]> {
    const myPorts = await this.getMyPortfolios();
    const portMap = new Map(myPorts.portfolios.map((p) => [p.id, p.name]));

    if (portfolioId === 'consolidated') {
      const allTxs = await Promise.all(
        myPorts.portfolios.map((p) =>
          apiClient.get<{ transactions: TransactionRecord[] }>(`/portfolio/${p.id}/transactions`)
        )
      );
      const combined = allTxs.flatMap((res) =>
        res.data.transactions.map((tx) => ({
          ...tx,
          portfolio_name: portMap.get(tx.portfolio_id) || 'Account',
        }))
      );
      return combined.sort((a, b) => new Date(b.executed_at).getTime() - new Date(a.executed_at).getTime());
    }

    const res = await apiClient.get<{ transactions: TransactionRecord[] }>(`/portfolio/${portfolioId}/transactions`);
    return res.data.transactions.map((tx) => ({
      ...tx,
      portfolio_name: portMap.get(tx.portfolio_id) || 'Account',
    }));
  },

  async createTransaction(
    portfolioId: string,
    payload: {
      transaction_type: string;
      symbol?: string;
      quantity?: number;
      price_per_share?: number;
      brokerage_fee?: number;
      executed_at?: string;
      notes?: string;
    }
  ): Promise<TransactionRecord> {
    const res = await apiClient.post<TransactionRecord>(`/portfolio/${portfolioId}/transactions`, payload);
    return res.data;
  },

  async deleteTransaction(portfolioId: string, transactionId: string): Promise<void> {
    await apiClient.delete(`/portfolio/${portfolioId}/transactions/${transactionId}`);
  },

  async updateTransaction(
    portfolioId: string,
    transactionId: string,
    payload: {
      symbol?: string;
      quantity?: number;
      price_per_share?: number;
      brokerage_fee?: number;
      notes?: string;
    }
  ): Promise<TransactionRecord> {
    const res = await apiClient.put<TransactionRecord>(
      `/portfolio/${portfolioId}/transactions/${transactionId}`,
      payload
    );
    return res.data;
  },

  async transferShares(payload: {
    from_portfolio_id: string;
    to_portfolio_id: string;
    symbol: string;
    quantity: number;
    cdc_transfer_fee?: number;
    notes?: string;
  }): Promise<void> {
    await apiClient.post('/portfolio/transfer-shares', payload);
  },

  async recordDividend(payload: {
    portfolio_id: string;
    symbol: string;
    dividend_per_share: number;
    tax_status: 'FILER' | 'NON_FILER' | 'CUSTOM';
    custom_tax_rate?: number;
    zakat_deducted?: number;
  }): Promise<void> {
    await apiClient.post('/corporate-actions/dividend', payload);
  },

  async getTaxReport(portfolioId: string, taxYear?: number): Promise<any> {
    const res = await apiClient.get(`/corporate-actions/tax-report/${portfolioId}`, {
      params: { tax_year: taxYear },
    });
    return res.data;
  },
};