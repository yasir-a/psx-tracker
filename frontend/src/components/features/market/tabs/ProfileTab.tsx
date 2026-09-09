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
      <div className="p-5 space-y-2 text-white shadow-sm bg-emerald-900 rounded-2xl">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-bold tracking-wider uppercase text-emerald-300">PSX Listed Company</span>
            <h2 className="text-2xl font-black">{name}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="bg-emerald-800 text-emerald-100 px-2.5 py-0.5 rounded text-xs font-bold">{symbol}</span>
              <span className="text-xs font-medium text-emerald-200">• {sector}</span>
            </div>
          </div>
          <Building2 className="w-12 h-12 text-emerald-400/40" />
        </div>
      </div>

      {/* Company Background */}
      <div className="p-5 space-y-3 bg-white border border-gray-200 rounded-2xl shadow-2xs">
        <h3 className="pb-2 text-sm font-bold tracking-wider text-gray-900 uppercase border-b">
          Company Background
        </h3>
        <p className="text-xs leading-relaxed text-justify text-gray-600">{p.background}</p>
      </div>

      {/* Equity Profile */}
      <div className="p-5 space-y-3 bg-white border border-gray-200 rounded-2xl shadow-2xs">
        <h3 className="pb-2 text-sm font-bold tracking-wider text-gray-900 uppercase border-b">
          Equity Profile
        </h3>
        <div className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
          <div className="p-3 border border-gray-100 bg-gray-50 rounded-xl">
            <span className="font-medium text-gray-500">Market Cap (Rs.):</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">
              Rs. {(p.market_cap / 1e9).toFixed(2)} Billion
            </div>
          </div>
          <div className="p-3 border border-gray-100 bg-gray-50 rounded-xl">
            <span className="font-medium text-gray-500">Total Shares:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{p.total_shares.toLocaleString()}</div>
          </div>
          <div className="p-3 border border-gray-100 bg-gray-50 rounded-xl">
            <span className="font-medium text-gray-500">Free Float Shares:</span>
            <div className="text-sm font-bold text-gray-900 mt-0.5">{p.free_float.toLocaleString()}</div>
          </div>
          <div className="p-3 border bg-emerald-50 rounded-xl border-emerald-200">
            <span className="font-medium text-emerald-800">Free Float (%):</span>
            <div className="text-sm font-black text-emerald-700 mt-0.5">{p.free_float_pct}%</div>
          </div>
        </div>
      </div>

      {/* Top Executives */}
      <div className="p-5 space-y-3 bg-white border border-gray-200 rounded-2xl shadow-2xs">
        <h3 className="pb-2 text-sm font-bold tracking-wider text-gray-900 uppercase border-b">
          Top Executives
        </h3>
        <div className="grid grid-cols-1 gap-3 text-xs sm:grid-cols-3">
          {p.executives.map((exec, idx) => (
            <div key={idx} className="flex items-center gap-3 p-3 border border-gray-100 bg-gray-50 rounded-xl">
              <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-emerald-100 text-emerald-800">
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
      <div className="p-5 space-y-3 text-xs bg-white border border-gray-200 rounded-2xl shadow-2xs">
        <h3 className="pb-2 text-sm font-bold tracking-wider text-gray-900 uppercase border-b">
          Contact & Statutory Information
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-1">
            <span className="flex items-center gap-1 font-semibold text-gray-400 uppercase">
              <MapPin className="w-3.5 h-3.5" /> Registered Head Office
            </span>
            <p className="font-medium text-gray-700">{p.address}</p>
          </div>

          <div className="space-y-1">
            <span className="flex items-center gap-1 font-semibold text-gray-400 uppercase">
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
            <span className="font-semibold text-gray-400 uppercase">Share Registrar</span>
            <p className="font-medium text-gray-700">{p.registrar}</p>
          </div>

          <div className="space-y-1">
            <span className="font-semibold text-gray-400 uppercase">Statutory Auditor</span>
            <p className="font-medium text-gray-700">{p.auditor}</p>
          </div>
        </div>
      </div>
    </div>
  );
};