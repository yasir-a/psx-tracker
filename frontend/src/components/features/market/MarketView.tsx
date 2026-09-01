import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { Input } from '../../ui/Input';
import { marketService } from '../../../services/marketService';
import { MarketQuote } from '../../../types/market';
import { SecurityDetailModal } from './SecurityDetailModal';
import { ChevronRight, BarChart2, Loader2 } from 'lucide-react';

export const MarketView: React.FC = () => {
  const [quotes, setQuotes] = useState<Record<string, MarketQuote>>({});
  const [query, setQuery] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const topCatalogSymbols = [
    'EFERT',
    'ENGRO',
    'SYS',
    'FFC',
    'OGDC',
    'LUCK',
    'HUBC',
    'MCB',
    'HBL',
    'MEBL',
    'PSO',
    'UBL',
    'BAFL',
    'MARI',
    'PPL',
    'MLCF',
    'DGKC',
    'ATRL',
    'AIRLINK',
    'TRG',
  ];

  useEffect(() => {
    const fetchQuotes = async () => {
      setIsLoading(true);
      try {
        const data = await marketService.getBulkQuotes(topCatalogSymbols);
        if (data && typeof data === 'object') {
          setQuotes(data);
        }
      } catch {
        // Silently handle error
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuotes();
  }, []);

  const filtered = Object.values(quotes).filter(
    (q): q is MarketQuote =>
      Boolean(
        q &&
          typeof q === 'object' &&
          typeof q.symbol === 'string' &&
          q.symbol.toLowerCase().includes(query.toLowerCase())
      )
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">PSX Market Data Terminal</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Click any security to launch interactive Live, Fundamentals, Technicals, Announcements & Profile terminal
          </p>
        </div>
      </div>

      <Card>
        <div className="mb-4 max-w-sm relative">
          <Input
            placeholder="Search symbol (e.g. EFERT, SYS, ENGRO)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center text-gray-500">
            <Loader2 className="w-8 h-8 animate-spin text-emerald-600 mb-3" />
            <p className="text-xs font-semibold">Fetching live quotes from Pakistan Stock Exchange...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-10 text-gray-500 text-sm">No securities found matching your search.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-gray-50 text-gray-500 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Current Price</th>
                  <th className="px-4 py-3">Previous Close</th>
                  <th className="px-4 py-3">Change (PKR)</th>
                  <th className="px-4 py-3">Change (%)</th>
                  <th className="px-4 py-3">Volume</th>
                  <th className="px-4 py-3 text-right">Analytics</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((q) => {
                  const isUp = (q.change || 0) >= 0;
                  return (
                    <tr
                      key={q.symbol}
                      onClick={() => setSelectedSymbol(q.symbol)}
                      className="hover:bg-emerald-50/50 transition-colors cursor-pointer group"
                    >
                      <td className="px-4 py-3.5 font-bold text-gray-900 group-hover:text-emerald-700 flex items-center gap-2">
                        <span className="bg-gray-100 text-gray-900 px-2 py-0.5 rounded border group-hover:bg-emerald-100 group-hover:border-emerald-300">
                          {q.symbol}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-bold text-gray-900">
                        PKR {(q.current_price || 0).toFixed(2)}
                      </td>
                      <td className="px-4 py-3.5 text-gray-600">
                        PKR {(q.previous_close || 0).toFixed(2)}
                      </td>
                      <td className={`px-4 py-3.5 font-medium ${isUp ? 'text-emerald-600' : 'text-rose-600'}`}>
                        {isUp ? '+' : ''}{(q.change || 0).toFixed(2)}
                      </td>
                      <td className="px-4 py-3.5">
                        <Badge variant={isUp ? 'green' : 'red'}>
                          {isUp ? '+' : ''}{(q.change_percent || 0).toFixed(2)}%
                        </Badge>
                      </td>
                      <td className="px-4 py-3.5 text-gray-500">{(q.volume || 0).toLocaleString()}</td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold text-emerald-700 bg-emerald-50 group-hover:bg-emerald-600 group-hover:text-white transition-colors border border-emerald-200">
                          <BarChart2 className="w-3.5 h-3.5" />
                          View Details
                          <ChevronRight className="w-3.5 h-3.5" />
                        </span>
                      </td>
                    </tr>
                  );
                })}
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