import React from 'react';
import { CompetitorItem } from '../../../../types/market';

interface CompetitorsTabProps {
  competitors: CompetitorItem[];
  sector: string;
  onSelectCompetitor: (symbol: string) => void;
}

export const CompetitorsTab: React.FC<CompetitorsTabProps> = ({
  competitors,
  sector,
  onSelectCompetitor,
}) => {
  return (
    <div className="p-5 space-y-4 bg-white border border-gray-200 rounded-2xl shadow-2xs">
      <div className="flex items-center justify-between pb-2 border-b">
        <h3 className="text-sm font-bold tracking-wider text-gray-900 uppercase">
          Sector Competitors & Peer Group
        </h3>
        <span className="text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded-md font-bold">
          {sector}
        </span>
      </div>

      {competitors.length === 0 ? (
        <div className="py-8 text-sm text-center text-gray-500">No direct peers available.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-xs font-semibold text-gray-500 uppercase bg-gray-50">
              <tr>
                <th className="px-4 py-3">Symbol</th>
                <th className="px-4 py-3">Company Name</th>
                <th className="px-4 py-3">Price (Rs.)</th>
                <th className="px-4 py-3">P/E Ratio</th>
                <th className="px-4 py-3">Market Cap (B)</th>
                <th className="px-4 py-3">Dividend Yield</th>
                <th className="px-4 py-3">1D Change</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {competitors.map((comp) => {
                const isUp = comp.change >= 0;
                return (
                  <tr key={comp.symbol} className="transition-colors hover:bg-gray-50/60">
                    <td className="px-4 py-3.5 font-bold text-gray-900">{comp.symbol}</td>
                    <td className="px-4 py-3.5 text-gray-700">{comp.name}</td>
                    <td className="px-4 py-3.5 font-semibold text-gray-900">Rs. {comp.price.toFixed(2)}</td>
                    <td className="px-4 py-3.5 text-gray-700">{comp.pe.toFixed(2)}</td>
                    <td className="px-4 py-3.5 text-gray-700">Rs. {(comp.market_cap / 1e9).toFixed(2)}B</td>
                    <td className="px-4 py-3.5 font-semibold text-emerald-700">{comp.dividend_yield.toFixed(2)}%</td>
                    <td className={`px-4 py-3.5 font-bold ${isUp ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {isUp ? '+' : ''}{comp.change}%
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        onClick={() => onSelectCompetitor(comp.symbol)}
                        className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition-colors"
                      >
                        Analyze
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};