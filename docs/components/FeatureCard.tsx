import React, { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  delay?: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description, delay = '0s' }) => {
  return (
    <div 
      className="p-8 rounded-2xl bg-white border border-zinc-200 hover:border-teal-200 hover:shadow-lg hover:shadow-teal-900/5 transition-all duration-300 group animate-slide-up"
      style={{ animationDelay: delay }}
    >
      <div className="w-12 h-12 bg-zinc-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-teal-50 transition-colors">
        <div className="text-zinc-600 group-hover:text-teal-600 transition-colors">
          {icon}
        </div>
      </div>
      <h3 className="text-lg font-bold text-zinc-900 mb-3 font-serif">{title}</h3>
      <p className="text-zinc-500 leading-relaxed text-sm font-light">
        {description}
      </p>
    </div>
  );
};