import React from 'react';
import { SecurityTechnicals } from '../../../../types/market';

interface TechnicalsTabProps {
  technicals: SecurityTechnicals;
}

const getSignalBadge = (signal: string) => {
  switch (signal) {
    case 'BUY':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'SELL':
      return 'bg-rose-50 text-rose-700 border-rose-200';
    default:
      return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

export const TechnicalsTab: React.FC<TechnicalsTabProps> = ({ technicals: t }) => {
  return (
    <div className="space-y-6">
      {/* Technical Indicators */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Technical Indicators
        </h3>
        <div className="divide-y divide-gray-100">
          {t.indicators.map((ind) => (
            <div key={ind.name} className="py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-gray-900">{ind.name}</span>
                <span className="text-xs text-gray-400">{ind.params}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono font-bold text-sm text-gray-800">{ind.value.toFixed(2)}</span>
                <span className={`px-2.5 py-1 text-[11px] font-bold rounded-md border uppercase ${getSignalBadge(ind.signal)}`}>
                  {ind.signal}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pivot Points (S3 -> R3) */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Pivot Points
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-7 gap-2 text-center text-xs">
          {Object.entries(t.pivot_points).map(([key, val]) => {
            const isResistance = key.startsWith('R');
            const isSupport = key.startsWith('S');
            const bgClass = isResistance
              ? 'bg-rose-50 border-rose-200 text-rose-800'
              : isSupport
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-gray-100 border-gray-300 text-gray-900 font-black';
            return (
              <div key={key} className={`p-2.5 rounded-xl border ${bgClass}`}>
                <div className="font-bold">{key}</div>
                <div className="font-mono font-bold mt-1">{val.toFixed(2)}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Simple Moving Averages */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Simple Moving Averages (SMA)
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
          {t.moving_averages.map((ma) => (
            <div key={ma.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
              <div>
                <span className="font-bold text-gray-900">{ma.name}</span>
                <span className="text-xs text-gray-400 block">{ma.label}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono font-bold text-gray-800">{ma.value.toFixed(2)}</span>
                <span className={`px-2 py-0.5 text-[11px] font-bold rounded-md border uppercase ${getSignalBadge(ma.signal)}`}>
                  {ma.signal}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};