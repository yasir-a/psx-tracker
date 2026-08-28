import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
}

export const Card: React.FC<CardProps> = ({ title, subtitle, children, className, ...props }) => {
  return (
    <div className={clsx('bg-white border border-gray-200 rounded-xl p-5 shadow-xs', className)} {...props}>
      {(title || subtitle) && (
        <div className="mb-4 pb-3 border-b border-gray-100">
          {title && <h3 className="text-base font-semibold text-gray-900">{title}</h3>}
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
};