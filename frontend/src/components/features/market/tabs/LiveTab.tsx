import React, { useState, useEffect, useRef } from 'react';
import { SecurityDetails } from '../../../../types/market';
import { marketService, HistoricalPriceBar } from '../../../../services/marketService';
import { Moon, Loader2 } from 'lucide-react';

interface LiveTabProps {
  data: SecurityDetails;
}

type TimeframeKey = '1D' | '1M' | '6M' | 'YTD' | '1Y' | '3Y' | '5Y';

interface ChartTick {
  time: string;
  price: number;
  volume: number;
}

export const LiveTab: React.FC<LiveTabProps> = ({ data }) => {
  const [timeframe, setTimeframe] = useState<TimeframeKey>('1D');
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const [historyCache, setHistoryCache] = useState<Record<string, ChartTick[]>>({});
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // 1D Ticks (default) from real backend intraday data
  const intradayTicks: ChartTick[] = React.useMemo(() => {
    if (data.intraday_ticks && data.intraday_ticks.length > 0) {
      return data.intraday_ticks;
    }
    if (data.intraday_points && data.intraday_points.length > 0) {
      return data.intraday_points.map((p, idx) => ({
        time: `Tick #${idx + 1}`,
        price: p,
        volume: data.volume,
      }));
    }
    return [
      { time: '09:30 AM', price: data.previous_close, volume: data.volume },
      { time: '03:30 PM', price: data.current_price, volume: data.volume },
    ];
  }, [data]);

  // Load real historical data when switching timeframes beyond 1D
  useEffect(() => {
    if (timeframe === '1D') return;

    if (historyCache[timeframe]) return; // Already cached in memory

    const fetchHistory = async () => {
      setIsLoadingHistory(true);
      try {
        let days = 30;
        const now = new Date();
        if (timeframe === '1M') days = 30;
        else if (timeframe === '6M') days = 180;
        else if (timeframe === 'YTD') {
          const startOfYear = new Date(now.getFullYear(), 0, 1);
          days = Math.ceil((now.getTime() - startOfYear.getTime()) / (1000 * 60 * 60 * 24)) + 5;
        } else if (timeframe === '1Y') days = 365;
        else if (timeframe === '3Y') days = 1095;
        else if (timeframe === '5Y') days = 1825;

        const bars: HistoricalPriceBar[] = await marketService.getHistoricalPrices(data.symbol, days);

        // Sort ascending by trade_date
        const sorted = [...bars].sort((a, b) => new Date(a.trade_date).getTime() - new Date(b.trade_date).getTime());
        const mapped: ChartTick[] = sorted.map((b) => ({
          time: new Date(b.trade_date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: timeframe === '3Y' || timeframe === '5Y' ? 'numeric' : undefined,
          }),
          price: b.close_price,
          volume: b.volume,
        }));

        if (mapped.length > 0) {
          setHistoryCache((prev) => ({ ...prev, [timeframe]: mapped }));
        }
      } catch (err) {
        console.error('Failed to load historical prices for timeframe:', timeframe, err);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    fetchHistory();
  }, [timeframe, data.symbol, historyCache]);

  // Active chart ticks based on selected timeframe
  const activeTicks = timeframe === '1D' ? intradayTicks : (historyCache[timeframe] || intradayTicks);

  const prices = activeTicks.map((t) => t.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceMargin = (maxPrice - minPrice) * 0.1 || 0.5;
  const chartMin = minPrice - priceMargin;
  const chartMax = maxPrice + priceMargin;
  const priceRange = chartMax - chartMin || 1;

  // 5 levels for Y-Axis labels
  const yTicks = [
    chartMax,
    chartMin + priceRange * 0.75,
    chartMin + priceRange * 0.5,
    chartMin + priceRange * 0.25,
    chartMin,
  ];

  // SVG Coordinates
  const coords = activeTicks.map((t, i) => {
    const x = (i / (activeTicks.length - 1 || 1)) * 100;
    const y = 90 - ((t.price - chartMin) / priceRange) * 80;
    return { x, y, ...t };
  });

  const linePath = coords.reduce(
    (acc, curr, i) => (i === 0 ? `M ${curr.x.toFixed(2)},${curr.y.toFixed(2)}` : `${acc} L ${curr.x.toFixed(2)},${curr.y.toFixed(2)}`),
    ''
  );
  const areaPath = `${linePath} L 100,100 L 0,100 Z`;

  const activeTick = hoverIndex !== null && coords[hoverIndex] ? coords[hoverIndex] : null;
  const isUp = activeTick ? activeTick.price >= (activeTicks[0]?.price || data.previous_close) : data.change >= 0;

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current || coords.length === 0) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
    const pct = mouseX / rect.width;
    const closestIdx = Math.round(pct * (coords.length - 1));
    setHoverIndex(closestIdx);
  };

  // Bottom Time Labels (start, middle, end)
  const labelStart = activeTicks[0]?.time || 'Start';
  const labelMid = activeTicks[Math.floor(activeTicks.length / 2)]?.time || 'Mid';
  const labelEnd = activeTicks[activeTicks.length - 1]?.time || 'End';

  return (
    <div className="space-y-6 text-gray-900">
      {/* Header Info */}
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-4xl font-extrabold tracking-tight text-gray-950">
            Rs.{activeTick ? activeTick.price.toFixed(2) : data.current_price.toFixed(2)}
          </span>
          <span className={`text-base font-bold ${isUp ? 'text-emerald-600' : 'text-rose-600'}`}>
            {isUp ? '▲ +' : '▼ '}{data.change.toFixed(2)} ({isUp ? '+' : ''}{data.change_percent.toFixed(2)}%)
          </span>
        </div>
        <div className="text-xs font-medium text-gray-500">
          ^ As of {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
        </div>
      </div>

      {/* Timeframe Selector (1D Default) */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1 p-1 bg-gray-100 border border-gray-200 rounded-lg">
          {(['1D', '1M', '6M', 'YTD', '1Y', '3Y', '5Y'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => {
                setTimeframe(tf);
                setHoverIndex(null);
              }}
              className={`px-3 py-1 rounded text-xs font-bold transition-all ${
                timeframe === tf
                  ? 'bg-emerald-700 text-white shadow-xs'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {data.is_shariah_compliant && (
          <span
            className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-md flex items-center gap-1.5 text-xs font-semibold"
            title="Shariah Compliant"
          >
            <Moon className="w-3.5 h-3.5 fill-emerald-600" />
            Shariah Compliant
          </span>
        )}
      </div>

      {/* PSX Terminal Style Chart Container */}
      <div className="relative p-4 border shadow-xs bg-amber-50/20 border-amber-200/80 rounded-xl">
        {isLoadingHistory && (
          <div className="absolute inset-0 z-30 flex items-center justify-center bg-white/70 backdrop-blur-xs rounded-xl">
            <Loader2 className="w-6 h-6 mr-2 animate-spin text-amber-600" />
            <span className="text-xs font-semibold text-gray-700">Loading {timeframe} PSX historical prices...</span>
          </div>
        )}

        <div
          ref={containerRef}
          className="relative w-full select-none h-72 cursor-crosshair"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoverIndex(null)}
        >
          {/* Background Grid Lines */}
          <div className="absolute inset-0 grid grid-cols-6 grid-rows-4 pointer-events-none">
            {[...Array(24)].map((_, i) => (
              <div key={i} className="border-b border-r border-amber-200/50" />
            ))}
          </div>

          {/* SVG Curve & Gradient Fill */}
          <svg
            className="absolute inset-0 w-full h-full"
            preserveAspectRatio="none"
            viewBox="0 0 100 100"
          >
            <defs>
              <linearGradient id="psxAmberGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#d97706" stopOpacity="0.30" />
                <stop offset="100%" stopColor="#fef3c7" stopOpacity="0.05" />
              </linearGradient>
            </defs>

            {/* Shaded Area Under Curve */}
            <path d={areaPath} fill="url(#psxAmberGradient)" />

            {/* Price Line Curve */}
            <path
              d={linePath}
              fill="none"
              stroke="#d97706"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Active Hover Point */}
            {activeTick && (
              <circle
                cx={activeTick.x}
                cy={activeTick.y}
                r="3.5"
                fill="#ffffff"
                stroke="#d97706"
                strokeWidth="2"
              />
            )}
          </svg>

          {/* Vertical Crosshair Line */}
          {activeTick && (
            <div
              className="absolute top-0 bottom-0 border-l pointer-events-none border-gray-400/80"
              style={{ left: `${activeTick.x}%` }}
            />
          )}

          {/* Right Y-Axis Price Labels */}
          <div className="absolute top-0 bottom-0 right-1 flex flex-col justify-between pointer-events-none text-[10px] font-mono font-semibold text-gray-500">
            {yTicks.map((p, idx) => (
              <span key={idx} className="px-1 rounded bg-amber-50/80">
                {p.toFixed(2)}
              </span>
            ))}
          </div>

          {/* Floating Tooltip Callout Box Matching Screenshot */}
          {activeTick && (
            <div
              className="absolute pointer-events-none bg-white border border-amber-400 rounded-lg shadow-lg p-2.5 z-20 text-xs transition-transform"
              style={{
                left: `${Math.min(75, Math.max(5, activeTick.x - 15))}%`,
                top: `${Math.max(5, activeTick.y - 25)}%`,
              }}
            >
              <div className="pb-1 mb-1 font-bold text-gray-900 border-b border-gray-100">
                {activeTick.time}
              </div>
              <div className="grid grid-cols-2 font-mono gap-x-4 gap-y-1">
                <span className="font-bold text-amber-600">{data.symbol}</span>
                <span className="font-black text-right text-gray-900">
                  {activeTick.price.toFixed(2)}
                </span>
                <span className="font-sans font-medium text-gray-500">Volume</span>
                <span className="text-right text-gray-800">
                  {activeTick.volume.toLocaleString()}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Time / Date Axis Labels */}
        <div className="flex justify-between px-2 pt-2 border-t border-amber-200/80 text-[11px] text-gray-500 font-medium">
          <span>{labelStart}</span>
          <span>{labelMid}</span>
          <span>{labelEnd}</span>
        </div>
      </div>
    </div>
  );
};