import React from 'react';
import { Card } from '../../ui/Card';
import { clsx } from 'clsx';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string;
  subValue?: string;
  isPositive?: boolean;
  isNeutral?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, subValue, isPositive, isNeutral }) => {
  return (
    <Card className="hover:border-gray-300 transition-colors">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
      {subValue && (
        <div className="flex items-center gap-1.5 mt-1.5">
          {!isNeutral && (
            isPositive ? (
              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5 text-rose-600" />
            )
          )}
          <span
            className={clsx(
              'text-xs font-medium',
              isNeutral ? 'text-gray-500' : isPositive ? 'text-emerald-600' : 'text-rose-600'
            )}
          >
            {subValue}
          </span>
        </div>
      )}
    </Card>
  );
};