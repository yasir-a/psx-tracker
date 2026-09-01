import React from 'react';
import { AnnouncementItem } from '../../../../types/market';
import { Download, ExternalLink } from 'lucide-react';

interface AnnouncementsTabProps {
  announcements: AnnouncementItem[];
}

export const AnnouncementsTab: React.FC<AnnouncementsTabProps> = ({ announcements }) => {
  return (
    <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-2xs space-y-4">
      <div className="flex items-center justify-between border-b pb-2">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900">
          Official PSX Filings & Disclosures
        </h3>
        <span className="text-xs text-gray-500 font-medium">{announcements.length} Total Announcements</span>
      </div>

      <div className="divide-y divide-gray-100">
        {announcements.map((item, idx) => (
          <div key={idx} className="py-3.5 flex items-start justify-between gap-4 hover:bg-gray-50/60 p-2 rounded-xl transition-colors">
            <div className="space-y-1 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold text-gray-500">{item.date} • {item.time}</span>
                <span className="bg-gray-100 text-gray-700 text-[10px] font-semibold px-2 py-0.5 rounded border">
                  {item.category}
                </span>
              </div>
              <h4 className="text-sm font-semibold text-gray-900 leading-snug">{item.title}</h4>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <a
                href={item.pdf_url}
                target="_blank"
                rel="noreferrer"
                className="p-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-colors inline-flex items-center gap-1 text-xs font-semibold"
                title="View announcement"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                VIEW
              </a>
              <a
                href={item.pdf_url}
                target="_blank"
                rel="noreferrer"
                className="p-1.5 rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition-colors inline-flex items-center gap-1 text-xs font-semibold"
                title="Download PDF filing"
              >
                <Download className="w-3.5 h-3.5" />
                PDF
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};