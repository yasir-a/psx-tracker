import React from 'react';
import { clsx } from 'clsx';

export const Skeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => {
  return <div className={clsx('animate-pulse bg-gray-200 rounded-md', className)} {...props} />;
};