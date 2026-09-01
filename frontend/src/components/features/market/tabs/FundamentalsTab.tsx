import React from 'react';
import { SecurityFundamentals } from '../../../../types/market';

interface FundamentalsTabProps {
  fundamentals: SecurityFundamentals;
}

export const FundamentalsTab: React.FC<FundamentalsTabProps> = ({ fundamentals: f }) => {
  return (
    <div className="space-y-6">
      {/* Earnings (EPS in Rs.) */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Earnings Per Share (EPS in Rs.)
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Annual 2025 FY</div>
            <div className="text-lg font-black text-gray-900 mt-1">{f.eps_annual.toFixed(2)}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Last Quarter (Q2)</div>
            <div className="text-lg font-black text-gray-900 mt-1">{f.eps_quarter.toFixed(2)}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Year-to-Date</div>
            <div className="text-lg font-black text-gray-900 mt-1">{f.eps_ytd.toFixed(2)}</div>
          </div>
          <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200">
            <div className="text-[10px] text-emerald-800 font-bold uppercase">Expected FY</div>
            <div className="text-lg font-black text-emerald-700 mt-1">{f.eps_expected.toFixed(2)}</div>
          </div>
        </div>

        {/* P/E Ratio & Growth */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">P/E (Annual 2025):</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{f.pe_annual.toFixed(2)}</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Expected P/E:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{f.pe_expected.toFixed(2)}</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Exp. Earning Growth:</span>
            <div className={`text-sm font-bold mt-0.5 ${f.expected_growth_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {f.expected_growth_pct.toFixed(2)}%
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">PEG Ratio:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{f.peg_ratio.toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Performance & Margins */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Performance & Profit Margins
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Gross Profit</div>
            <div className="text-base font-bold text-gray-900 mt-1">{f.gross_profit_pct.toFixed(2)}%</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Operating Profit</div>
            <div className="text-base font-bold text-gray-900 mt-1">{f.operating_profit_pct.toFixed(2)}%</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Net Profit</div>
            <div className="text-base font-bold text-emerald-700 mt-1">{f.net_profit_pct.toFixed(2)}%</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">EBITDA</div>
            <div className="text-base font-bold text-gray-900 mt-1">{f.ebitda_pct.toFixed(2)}%</div>
          </div>
        </div>

        {/* Return On Capital */}
        <div className="grid grid-cols-3 gap-3 text-center pt-2">
          <div className="p-3 bg-emerald-50 text-emerald-900 rounded-xl border border-emerald-200">
            <div className="text-[10px] font-bold uppercase">Equity (ROE)</div>
            <div className="text-base font-black mt-1">{f.roe_pct.toFixed(2)}%</div>
          </div>
          <div className="p-3 bg-blue-50 text-blue-900 rounded-xl border border-blue-200">
            <div className="text-[10px] font-bold uppercase">Assets (ROA)</div>
            <div className="text-base font-black mt-1">{f.roa_pct.toFixed(2)}%</div>
          </div>
          <div className="p-3 bg-purple-50 text-purple-900 rounded-xl border border-purple-200">
            <div className="text-[10px] font-bold uppercase">Cap Employed (ROCE)</div>
            <div className="text-base font-black mt-1">{f.roce_pct.toFixed(2)}%</div>
          </div>
        </div>
      </div>

      {/* Payouts & Dividends */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Payouts & Dividend History (DPS in Rs.)
        </h3>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Annual 2025 FY</div>
            <div className="text-lg font-black text-gray-900 mt-1">Rs. {f.dps_annual.toFixed(2)}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-500 font-bold uppercase">Last Quarter (Q2)</div>
            <div className="text-lg font-black text-gray-900 mt-1">Rs. {f.dps_quarter.toFixed(2)}</div>
          </div>
          <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200">
            <div className="text-[10px] text-emerald-800 font-bold uppercase">Last Interim</div>
            <div className="text-lg font-black text-emerald-700 mt-1">Rs. {f.dps_interim.toFixed(2)}</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 text-xs pt-2">
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Dividend Yield:</span>
            <div className="text-sm font-bold text-emerald-700 mt-0.5">{f.dividend_yield_pct.toFixed(2)}%</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Dividend Cover:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{f.dividend_cover.toFixed(2)}x</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Payout Ratio:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{f.payout_ratio_pct.toFixed(2)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
};