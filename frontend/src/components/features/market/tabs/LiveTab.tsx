import React, { useState } from 'react';
import { SecurityDetails } from '../../../../types/market';
import { Camera, Moon } from 'lucide-react';

interface LiveTabProps {
  data: SecurityDetails;
}

export const LiveTab: React.FC<LiveTabProps> = ({ data }) => {
  const [timeframe, setTimeframe] = useState<'1D' | '1M' | '6M' | 'YTD' | '1Y' | '3Y' | '5Y'>('1D');

  const isUp = data.change >= 0;

  // Day range slider percentage calculation
  const dayRangeSpan = data.day_high - data.day_low || 1;
  const dayRangePct = Math.min(100, Math.max(0, ((data.current_price - data.day_low) / dayRangeSpan) * 100));

  // 52-week slider calculation
  const yearRangeSpan = data.week_52_high - data.week_52_low || 1;
  const yearRangePct = Math.min(100, Math.max(0, ((data.current_price - data.week_52_low) / yearRangeSpan) * 100));

  return (
    <div className="space-y-6 text-gray-900">
      {/* Price Header Card */}
      <div className="bg-gray-950 text-white p-5 rounded-2xl border border-gray-800 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-black tracking-tight text-white">
                {data.current_price.toFixed(2)}
              </span>
              <span className={`text-base font-bold flex items-center ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isUp ? '▲ +' : '▼ '}{data.change.toFixed(2)} ({isUp ? '+' : ''}{data.change_percent.toFixed(2)}%)
              </span>
            </div>
            <div className="text-[11px] text-gray-400 mt-1 flex items-center gap-1.5">
              <span>🕒 {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="bg-gray-800 text-gray-300 text-xs font-bold px-2.5 py-1 rounded-md border border-gray-700">
              {data.market_status || 'REG'}
            </span>
            {data.is_shariah_compliant && (
              <span className="bg-emerald-950 text-emerald-400 border border-emerald-700/60 p-1.5 rounded-md flex items-center gap-1 text-xs font-medium" title="Shariah Compliant">
                <Moon className="w-3.5 h-3.5 fill-emerald-400" />
              </span>
            )}
          </div>
        </div>

        {/* Intraday Chart Graphic Representation */}
        <div className="mt-6 pt-4 border-t border-gray-800">
          <div className="h-44 w-full flex items-end justify-between gap-1 px-2 py-4 bg-gray-900/60 rounded-xl relative overflow-hidden">
            {/* SVG Wave Line */}
            <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
              <path
                d="M 0,60 Q 20,40 40,55 T 80,30 T 100,70 L 100,100 L 0,100 Z"
                fill={isUp ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)'}
              />
              <path
                d="M 0,60 Q 20,40 40,55 T 80,30 T 100,70"
                fill="none"
                stroke={isUp ? '#10b981' : '#f43f5e'}
                strokeWidth="2.5"
              />
            </svg>
          </div>

          {/* Timeframe selector pills */}
          <div className="flex justify-between items-center mt-3 pt-2 border-t border-gray-800">
            <div className="flex gap-1">
              {(['1D', '1M', '6M', 'YTD', '1Y', '3Y', '5Y'] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                    timeframe === tf
                      ? 'bg-amber-500 text-gray-950'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>

            <button
              onClick={() => alert('Screenshot captured!')}
              className="inline-flex items-center gap-1.5 px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded-lg transition-colors border border-gray-700"
            >
              <Camera className="w-3.5 h-3.5" />
              Share Screenshot
            </button>
          </div>
        </div>
      </div>

      {/* Stats Summary Card */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-5">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Market Stats
        </h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[11px] text-gray-500 font-semibold uppercase">Volume</div>
            <div className="text-base font-bold text-gray-900 mt-0.5">{data.volume.toLocaleString()}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[11px] text-gray-500 font-semibold uppercase">Open Price</div>
            <div className="text-base font-bold text-gray-900 mt-0.5">PKR {data.open_price.toFixed(2)}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[11px] text-gray-500 font-semibold uppercase">Last Day</div>
            <div className="text-base font-bold text-gray-900 mt-0.5">PKR {data.previous_close.toFixed(2)}</div>
          </div>
        </div>

        {/* Latest Quote (Bid / Ask) */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">Latest Order Book Quote</h4>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="flex justify-between p-2.5 bg-emerald-50 text-emerald-900 rounded-lg border border-emerald-200">
              <span className="font-semibold">Bid: PKR {data.bid_price.toFixed(2)}</span>
              <span className="font-medium text-emerald-700">Vol: {data.bid_volume.toLocaleString()}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-rose-50 text-rose-900 rounded-lg border border-rose-200">
              <span className="font-semibold">Ask: PKR {data.ask_price.toFixed(2)}</span>
              <span className="font-medium text-rose-700">Vol: {data.ask_volume.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Day's Range Slider */}
        <div className="space-y-1.5 pt-2">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-gray-500 uppercase tracking-wider">Day's Range</span>
          </div>
          <div className="relative pt-4 pb-2">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: `${dayRangePct}%` }}></div>
            </div>
            <div
              className="absolute top-0 transform -translate-x-1/2 flex flex-col items-center"
              style={{ left: `${dayRangePct}%` }}
            >
              <span className="text-[10px] font-bold bg-gray-900 text-white px-1.5 py-0.5 rounded shadow-xs">
                {data.current_price.toFixed(2)}
              </span>
              <div className="w-1.5 h-1.5 bg-gray-900 rotate-45 -mt-0.5"></div>
            </div>
          </div>
          <div className="flex justify-between text-xs font-bold text-gray-700">
            <span>Low: PKR {data.day_low.toFixed(2)}</span>
            <span>High: PKR {data.day_high.toFixed(2)}</span>
          </div>
        </div>

        {/* 52-Week Range Slider */}
        <div className="space-y-1.5 pt-2 border-t border-gray-100">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-gray-500 uppercase tracking-wider">52-Week Range</span>
          </div>
          <div className="relative pt-4 pb-2">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${yearRangePct}%` }}></div>
            </div>
            <div
              className="absolute top-0 transform -translate-x-1/2 flex flex-col items-center"
              style={{ left: `${yearRangePct}%` }}
            >
              <span className="text-[10px] font-bold bg-rose-600 text-white px-1.5 py-0.5 rounded shadow-xs">
                {data.current_price.toFixed(2)}
              </span>
              <div className="w-1.5 h-1.5 bg-rose-600 rotate-45 -mt-0.5"></div>
            </div>
          </div>
          <div className="flex justify-between text-xs font-bold text-gray-700">
            <span>52W Low: PKR {data.week_52_low.toFixed(2)}</span>
            <span>52W High: PKR {data.week_52_high.toFixed(2)}</span>
          </div>
        </div>

        {/* Circuit Breakers */}
        <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs flex justify-between items-center text-amber-900 font-semibold">
          <span>Circuit Breakers (Lower / Upper Lock)</span>
          <span className="font-bold">PKR {data.circuit_lower.toFixed(2)} — PKR {data.circuit_upper.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};