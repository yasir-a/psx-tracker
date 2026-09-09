import React, { useState, useMemo } from 'react';
import { Holding } from '../../../types/portfolio';
import { Card } from '../../ui/Card';
import { PieChart, Building2, Layers } from 'lucide-react';
import { clsx } from 'clsx';

interface PortfolioBreakdownProps {
  holdings: Holding[];
  portfolioName: string;
}

type BreakdownTab = 'company' | 'sector';

interface SliceItem {
  id: string;
  label: string;
  subLabel?: string;
  value: number;
  percentage: number;
  color: string;
}

// Accessible, distinctive color palette for financial charts
const PALETTE = [
  '#059669', // Emerald
  '#2563eb', // Blue
  '#d97706', // Amber
  '#7c3aed', // Purple
  '#0891b2', // Cyan
  '#dc2626', // Rose
  '#ea580c', // Orange
  '#4f46e5', // Indigo
  '#16a34a', // Green
  '#64748b', // Slate
];

export const PortfolioBreakdown: React.FC<PortfolioBreakdownProps> = ({
  holdings,
  portfolioName,
}) => {
  const [activeTab, setActiveTab] = useState<BreakdownTab>('company');
  const [hoveredSliceId, setHoveredSliceId] = useState<string | null>(null);

  // Total Stock Market Value
  const totalStockValue = useMemo(() => {
    return holdings.reduce((sum, h) => sum + (h.market_value > 0 ? h.market_value : 0), 0);
  }, [holdings]);

  // Slices by Company
  const companySlices: SliceItem[] = useMemo(() => {
    if (totalStockValue <= 0) return [];

    // Aggregate by symbol (guarantees combined numbers for All Accounts)
    const agg: Record<string, { name: string; value: number }> = {};
    for (const h of holdings) {
      if (h.market_value <= 0) continue;
      if (!agg[h.symbol]) {
        agg[h.symbol] = { name: h.name || `${h.symbol} Limited`, value: 0 };
      }
      agg[h.symbol].value += h.market_value;
    }

    const sorted = Object.entries(agg)
      .map(([sym, data]) => ({
        id: sym,
        label: sym,
        subLabel: data.name,
        value: data.value,
        percentage: (data.value / totalStockValue) * 100,
      }))
      .sort((a, b) => b.value - a.value);

    // Group small allocations (< 2.5% or beyond top 7) into 'Others' if list is long
    if (sorted.length > 7) {
      const top = sorted.slice(0, 6);
      const remaining = sorted.slice(6);
      const othersVal = remaining.reduce((sum, r) => sum + r.value, 0);

      const items: SliceItem[] = top.map((item, idx) => ({
        ...item,
        color: PALETTE[idx % PALETTE.length],
      }));

      if (othersVal > 0) {
        items.push({
          id: 'others',
          label: 'Others',
          subLabel: `${remaining.length} smaller holdings`,
          value: othersVal,
          percentage: (othersVal / totalStockValue) * 100,
          color: '#94a3b8',
        });
      }
      return items;
    }

    return sorted.map((item, idx) => ({
      ...item,
      color: PALETTE[idx % PALETTE.length],
    }));
  }, [holdings, totalStockValue]);

  // Slices by Sector
  const sectorSlices: SliceItem[] = useMemo(() => {
    if (totalStockValue <= 0) return [];

    const agg: Record<string, number> = {};
    for (const h of holdings) {
      if (h.market_value <= 0) continue;
      const sec = h.sector?.trim() || 'Miscellaneous';
      agg[sec] = (agg[sec] || 0) + h.market_value;
    }

    const sorted = Object.entries(agg)
      .map(([sec, val]) => ({
        id: sec,
        label: sec,
        value: val,
        percentage: (val / totalStockValue) * 100,
      }))
      .sort((a, b) => b.value - a.value);

    // Group if more than 7 sectors
    if (sorted.length > 7) {
      const top = sorted.slice(0, 6);
      const remaining = sorted.slice(6);
      const othersVal = remaining.reduce((sum, r) => sum + r.value, 0);

      const items: SliceItem[] = top.map((item, idx) => ({
        ...item,
        color: PALETTE[idx % PALETTE.length],
      }));

      if (othersVal > 0) {
        items.push({
          id: 'others-sector',
          label: 'Others',
          subLabel: `${remaining.length} sectors`,
          value: othersVal,
          percentage: (othersVal / totalStockValue) * 100,
          color: '#94a3b8',
        });
      }
      return items;
    }

    return sorted.map((item, idx) => ({
      ...item,
      color: PALETTE[idx % PALETTE.length],
    }));
  }, [holdings, totalStockValue]);

  const activeSlices = activeTab === 'company' ? companySlices : sectorSlices;
  const activeHovered = activeSlices.find((s) => s.id === hoveredSliceId) || null;

  // Compute SVG Donut Paths using viewBox="0 0 100 100" (center 50,50, radius 40)
  const radius = 38;
  const innerRadius = 24;
  const center = 50;

  let cumulativeAngle = 0;
  const donutPaths = activeSlices.map((slice) => {
    const sliceAngle = (slice.percentage / 100) * 360;
    const startAngle = cumulativeAngle;
    const endAngle = cumulativeAngle + sliceAngle;
    cumulativeAngle = endAngle;

    // Convert polar to cartesian
    const toRad = (deg: number) => ((deg - 90) * Math.PI) / 180;

    const x1 = center + radius * Math.cos(toRad(startAngle));
    const y1 = center + radius * Math.sin(toRad(startAngle));
    const x2 = center + radius * Math.cos(toRad(endAngle));
    const y2 = center + radius * Math.sin(toRad(endAngle));

    const ix1 = center + innerRadius * Math.cos(toRad(endAngle));
    const iy1 = center + innerRadius * Math.sin(toRad(endAngle));
    const ix2 = center + innerRadius * Math.cos(toRad(startAngle));
    const iy2 = center + innerRadius * Math.sin(toRad(startAngle));

    const largeArcFlag = sliceAngle > 180 ? 1 : 0;

    // SVG donut slice path
    const pathData = [
      `M ${x1.toFixed(2)} ${y1.toFixed(2)}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`,
      `L ${ix1.toFixed(2)} ${iy1.toFixed(2)}`,
      `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${ix2.toFixed(2)} ${iy2.toFixed(2)}`,
      'Z',
    ].join(' ');

    return {
      ...slice,
      pathData,
    };
  });

  return (
    <Card className="flex flex-col justify-between h-full">
      {/* Header & Tab Selector */}
      <div>
        <div className="flex flex-col justify-between gap-2 pb-3 border-b border-gray-100 sm:flex-row sm:items-center">
          <div>
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
              <PieChart className="w-4 h-4 text-emerald-600" />
              {portfolioName} Breakdown
            </h3>
            <p className="text-[11px] text-gray-500">
              Asset allocation weighted by current market value
            </p>
          </div>

          {/* By Company / By Sector Tabs */}
          <div className="flex p-0.5 bg-gray-100 rounded-lg self-start sm:self-auto">
            <button
              onClick={() => {
                setActiveTab('company');
                setHoveredSliceId(null);
              }}
              className={clsx(
                'flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-md transition-all',
                activeTab === 'company'
                  ? 'bg-white text-gray-900 shadow-2xs'
                  : 'text-gray-500 hover:text-gray-900'
              )}
            >
              <Building2 className="w-3.5 h-3.5" />
              By Company
            </button>
            <button
              onClick={() => {
                setActiveTab('sector');
                setHoveredSliceId(null);
              }}
              className={clsx(
                'flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-md transition-all',
                activeTab === 'sector'
                  ? 'bg-white text-gray-900 shadow-2xs'
                  : 'text-gray-500 hover:text-gray-900'
              )}
            >
              <Layers className="w-3.5 h-3.5" />
              By Sector
            </button>
          </div>
        </div>

        {/* Content Body */}
        {totalStockValue <= 0 || activeSlices.length === 0 ? (
          <div className="py-12 text-center text-gray-400">
            <PieChart className="w-10 h-10 mx-auto mb-2 text-gray-300 stroke-1" />
            <p className="text-xs font-medium text-gray-600">No active stock holdings in this portfolio</p>
            <p className="text-[11px] text-gray-400 mt-0.5">
              Execute a BUY trade or transfer shares to view allocation charts.
            </p>
          </div>
        ) : (
          <div className="grid items-center grid-cols-1 gap-5 pt-4 md:grid-cols-12">
            {/* Donut Chart Visual */}
            <div className="relative flex justify-center md:col-span-5">
              <div className="relative w-44 h-44">
                <svg
                  viewBox="0 0 100 100"
                  className="w-full h-full transform -rotate-90 filter drop-shadow-xs"
                >
                  {donutPaths.map((slice) => {
                    const isHovered = hoveredSliceId === slice.id;
                    return (
                      <path
                        key={slice.id}
                        d={slice.pathData}
                        fill={slice.color}
                        className="transition-all duration-200 cursor-pointer"
                        opacity={hoveredSliceId && !isHovered ? 0.45 : 1}
                        stroke="#ffffff"
                        strokeWidth={isHovered ? '1.5' : '0.8'}
                        transform={isHovered ? 'scale(1.03) translate(-1.5, -1.5)' : undefined}
                        onMouseEnter={() => setHoveredSliceId(slice.id)}
                        onMouseLeave={() => setHoveredSliceId(null)}
                      />
                    );
                  })}
                </svg>

                {/* Center Callout inside Donut */}
                <div className="absolute inset-0 flex flex-col items-center justify-center p-2 text-center pointer-events-none">
                  {activeHovered ? (
                    <>
                      <span className="text-[10px] font-bold text-gray-500 uppercase truncate max-w-[85px]">
                        {activeHovered.label}
                      </span>
                      <span className="font-mono text-sm font-black text-gray-900">
                        {activeHovered.percentage.toFixed(1)}%
                      </span>
                      <span className="text-[9px] text-gray-500 font-mono">
                        Rs. {(activeHovered.value / 1000).toFixed(0)}k
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="text-[9px] font-semibold text-gray-400 uppercase tracking-wider">
                        Total Stock
                      </span>
                      <span className="font-mono text-xs font-black text-gray-900">
                        Rs. {(totalStockValue / 1000).toFixed(0)}k
                      </span>
                      <span className="text-[9px] text-emerald-600 font-semibold">
                        {holdings.length} {holdings.length === 1 ? 'Holding' : 'Holdings'}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Slices Legend List */}
            <div className="md:col-span-7 space-y-1.5 max-h-56 overflow-y-auto pr-1">
              {activeSlices.map((slice) => {
                const isHovered = hoveredSliceId === slice.id;
                return (
                  <div
                    key={slice.id}
                    onMouseEnter={() => setHoveredSliceId(slice.id)}
                    onMouseLeave={() => setHoveredSliceId(null)}
                    className={clsx(
                      'flex items-center justify-between p-1.5 rounded-lg text-xs cursor-pointer transition-colors',
                      isHovered ? 'bg-gray-100' : 'hover:bg-gray-50'
                    )}
                  >
                    <div className="flex items-center min-w-0 gap-2 pr-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: slice.color }}
                      />
                      <div className="truncate">
                        <span className="font-bold text-gray-900">{slice.label}</span>
                        {slice.subLabel && (
                          <span className="text-[10px] text-gray-400 ml-1.5 hidden sm:inline truncate">
                            {slice.subLabel}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 text-right shrink-0">
                      <span className="font-mono text-gray-600 text-[11px]">
                        Rs. {slice.value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </span>
                      <span className="w-12 font-mono font-bold text-right text-gray-900">
                        {slice.percentage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-500">
        <span>Allocation: {activeTab === 'company' ? 'By Company' : 'By PSX Sector'}</span>
        <span className="font-mono font-semibold text-gray-700">
          Total: Rs. {totalStockValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      </div>
    </Card>
  );
};