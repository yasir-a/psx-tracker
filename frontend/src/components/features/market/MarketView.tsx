import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { Input } from '../../ui/Input';
import { marketService } from '../../../services/marketService';
import { MarketQuote } from '../../../types/market';

export const MarketView: React.FC = () => {
  const [quotes, setQuotes] = useState<Record<string, MarketQuote>>({});
  const [query, setQuery] = useState('');

  const defaultSymbols = ['ENGRO', 'SYS', 'OGDC', 'LUCK', 'HUBC', 'MCB', 'FFC', 'HBL', 'MEBL', 'PSO'];

  useEffect(() => {
    const fetchQuotes = async () => {
      try {
        const data = await marketService.getBulkQuotes(defaultSymbols);
        setQuotes(data);
      } catch {
        // Handle error
      }
    };
    fetchQuotes();
  }, []);

  const filtered = Object.values(quotes).filter((q) =>
    q.symbol.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">PSX Market Data</h2>
          <p className="text-xs text-gray-500 mt-0.5">Real-time quotes with Redis caching layer</p>
        </div>
      </div>

      <Card>
        <div className="mb-4 max-w-xs">
          <Input
            placeholder="Search symbol (e.g. ENGRO)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-10 text-gray-500 text-sm">No securities found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs font-semibold uppercase">
                <tr>
                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Current Price</th>
                  <th className="px-4 py-3">Previous Close</th>
                  <th className="px-4 py-3">Change (PKR)</th>
                  <th className="px-4 py-3">Change (%)</th>
                  <th className="px-4 py-3">Volume</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((q) => {
                  const isUp = q.change >= 0;
                  return (
                    <tr key={q.symbol} className="hover:bg-gray-50/60 transition-colors">
                      <td className="px-4 py-3.5 font-bold text-gray-900">{q.symbol}</td>
                      <td className="px-4 py-3.5 font-semibold text-gray-900">PKR {q.current_price.toFixed(2)}</td>
                      <td className="px-4 py-3.5 text-gray-600">PKR {q.previous_close.toFixed(2)}</td>
                      <td className={`px-4 py-3.5 font-medium ${isUp ? 'text-emerald-600' : 'text-rose-600'}`}>
                        {isUp ? '+' : ''}{q.change.toFixed(2)}
                      </td>
                      <td className="px-4 py-3.5">
                        <Badge variant={isUp ? 'green' : 'red'}>
                          {isUp ? '+' : ''}{q.change_percent}%
                        </Badge>
                      </td>
                      <td className="px-4 py-3.5 text-gray-500">{q.volume.toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};