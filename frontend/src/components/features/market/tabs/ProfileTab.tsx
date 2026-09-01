import React from 'react';
import { CompanyProfile } from '../../../../types/market';
import { ExternalLink, Building2, User, Globe, MapPin } from 'lucide-react';

interface ProfileTabProps {
  profile: CompanyProfile;
  symbol: string;
  name: string;
  sector: string;
}

export const ProfileTab: React.FC<ProfileTabProps> = ({ profile: p, symbol, name, sector }) => {
  return (
    <div className="space-y-6 text-gray-900">
      {/* Header Info */}
      <div className="bg-emerald-900 text-white p-5 rounded-2xl shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs uppercase font-bold text-emerald-300 tracking-wider">PSX Listed Company</span>
            <h2 className="text-2xl font-black">{name}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="bg-emerald-800 text-emerald-100 px-2.5 py-0.5 rounded text-xs font-bold">{symbol}</span>
              <span className="text-xs text-emerald-200 font-medium">• {sector}</span>
            </div>
          </div>
          <Building2 className="w-12 h-12 text-emerald-400/40" />
        </div>
      </div>

      {/* Company Background */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Company Background
        </h3>
        <p className="text-xs text-gray-600 leading-relaxed text-justify">{p.background}</p>
      </div>

      {/* Equity Profile */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Equity Profile
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Market Cap (PKR):</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">
              Rs. {(p.market_cap / 1e9).toFixed(2)} Billion
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Total Shares:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{p.total_shares.toLocaleString()}</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-gray-500 font-medium">Free Float Shares:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{p.free_float.toLocaleString()}</div>
          </div>
          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
            <span className="text-emerald-800 font-medium">Free Float (%):</span>
            <div className="text-sm font-black text-emerald-700 mt-0.5">{p.free_float_pct}%</div>
          </div>
        </div>
      </div>

      {/* Top Executives */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Top Executives
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          {p.executives.map((exec, idx) => (
            <div key={idx} className="p-3 bg-gray-50 rounded-xl border border-gray-100 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                <User className="w-4 h-4" />
              </div>
              <div>
                <span className="text-gray-400 block text-[10px] uppercase font-bold">{exec.title}</span>
                <span className="text-sm font-bold text-gray-900">{exec.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Contact & Statutory Information */}
      <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-3 text-xs">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 border-b pb-2">
          Contact & Statutory Information
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <span className="text-gray-400 font-semibold uppercase flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" /> Registered Head Office
            </span>
            <p className="text-gray-700 font-medium">{p.address}</p>
          </div>

          <div className="space-y-1">
            <span className="text-gray-400 font-semibold uppercase flex items-center gap-1">
              <Globe className="w-3.5 h-3.5" /> Official Website
            </span>
            <div>
              <a
                href={p.website}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500 hover:bg-amber-600 text-gray-950 font-bold rounded-lg transition-colors text-xs"
              >
                Visit Website
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-gray-400 font-semibold uppercase">Share Registrar</span>
            <p className="text-gray-700 font-medium">{p.registrar}</p>
          </div>

          <div className="space-y-1">
            <span className="text-gray-400 font-semibold uppercase">Statutory Auditor</span>
            <p className="text-gray-700 font-medium">{p.auditor}</p>
          </div>
        </div>
      </div>
    </div>
  );
};