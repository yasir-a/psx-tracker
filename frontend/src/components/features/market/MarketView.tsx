import React, { useState } from 'react';
import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { Input } from '../../ui/Input';
import { Button } from '../../ui/Button';
import { marketService } from '../../../services/marketService';
import { MarketQuote } from '../../../types/market';
import { SecurityDetailModal } from './SecurityDetailModal';
import { ChevronRight, BarChart2, Loader2, Search } from 'lucide-react';

export const MarketView: React.FC = () => {
  const [quote, setQuote] = useState<MarketQuote | null>(null);
  const [query, setQuery] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const symbolToSearch = query.trim().toUpperCase();
    if (!symbolToSearch) return;

    setIsLoading(true);
    setErrorMessage(null);
    setHasSearched(true);

    try {
      const data = await marketService.getQuote(symbolToSearch);
      if (data && data.symbol) {
        setQuote(data);
      } else {
        setQuote(null);
        setErrorMessage(`Symbol "${symbolToSearch}" was not found on PSX.`);
      }
    } catch (err: any) {
      setQuote(null);
      setErrorMessage(
        err?.response?.data?.error?.message ||
          `Failed to fetch quote for "${symbolToSearch}". Please check the symbol and try again.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const isUp = (quote?.change || 0) >= 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">PSX Market Data Terminal</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Search any PSX symbol and press Enter to view real-time quote, technicals, and fundamentals
          </p>
        </div>
      </div>

      <Card>
        {/* Search Input Bar with Enter Submit */}
        <form onSubmit={handleSearch} className="flex max-w-md gap-2 mb-6">
          <div className="relative flex-1">
            <Input
              placeholder="Enter PSX symbol and hit Enter (e.g. EFERT, SYS, ENGRO)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />
          </div>
          <Button type="submit" variant="primary" disabled={!query.trim() || isLoading}>
            <Search className="w-4 h-4 mr-1" />
            Search
          </Button>
        </form>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16 text-gray-500">
            <Loader2 className="w-8 h-8 mb-3 animate-spin text-emerald-600" />
            <p className="text-xs font-semibold">
              Fetching live quote for {query.toUpperCase()} from Pakistan Stock Exchange...
            </p>
          </div>
        ) : errorMessage ? (
          <div className="py-12 text-sm font-medium text-center border text-rose-600 bg-rose-50/50 rounded-xl border-rose-100">
            {errorMessage}
          </div>
        ) : !hasSearched || !quote ? (
          <div className="py-16 text-sm text-center text-gray-400">
            <Search className="w-10 h-10 mx-auto mb-3 text-gray-300" />
            <p className="font-medium text-gray-600">No symbol searched yet</p>
            <p className="mt-1 text-xs text-gray-400">
              Type a stock ticker like <span className="font-semibold text-emerald-700">EFERT</span>,{' '}
              <span className="font-semibold text-emerald-700">SYS</span>, or{' '}
              <span className="font-semibold text-emerald-700">ENGRO</span> and hit Enter.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="text-xs font-semibold tracking-wider text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Current Price</th>
                  <th className="px-4 py-3">Previous Close</th>
                  <th className="px-4 py-3">Change (Rs.)</th>
                  <th className="px-4 py-3">Change (%)</th>
                  <th className="px-4 py-3">Volume</th>
                  <th className="px-4 py-3 text-right">Analytics</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                <tr
                  onClick={() => setSelectedSymbol(quote.symbol)}
                  className="transition-colors cursor-pointer hover:bg-emerald-50/50 group"
                >
                  <td className="px-4 py-3.5 font-bold text-gray-900 group-hover:text-emerald-700 flex items-center gap-2">
                    <span className="bg-gray-100 text-gray-900 px-2.5 py-1 rounded-md border text-xs font-bold group-hover:bg-emerald-100 group-hover:border-emerald-300">
                      {quote.symbol}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 font-bold text-gray-900">
                    Rs. {(quote.current_price || 0).toFixed(2)}
                  </td>
                  <td className="px-4 py-3.5 text-gray-600">
                    Rs. {(quote.previous_close || 0).toFixed(2)}
                  </td>
                  <td className={`px-4 py-3.5 font-medium ${isUp ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {isUp ? '+' : ''}{(quote.change || 0).toFixed(2)}
                  </td>
                  <td className="px-4 py-3.5">
                    <Badge variant={isUp ? 'green' : 'red'}>
                      {isUp ? '+' : ''}{(quote.change_percent || 0).toFixed(2)}%
                    </Badge>
                  </td>
                  <td className="px-4 py-3.5 text-gray-500">{(quote.volume || 0).toLocaleString()}</td>
                  <td className="px-4 py-3.5 text-right">
                    <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-bold transition-colors border rounded-lg text-emerald-700 bg-emerald-50 group-hover:bg-emerald-600 group-hover:text-white border-emerald-200 shadow-2xs">
                      <BarChart2 className="w-3.5 h-3.5" />
                      View Details
                      <ChevronRight className="w-3.5 h-3.5" />
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* 6-Tab Security Detail Terminal Modal */}
      <SecurityDetailModal
        symbol={selectedSymbol}
        isOpen={!!selectedSymbol}
        onClose={() => setSelectedSymbol(null)}
      />
    </div>
  );
};