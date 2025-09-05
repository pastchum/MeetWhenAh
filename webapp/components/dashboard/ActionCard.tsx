import React from 'react';

interface ActionCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  iconBgColor: string;
  iconColor: string;
  onClick: () => void;
}

export default function ActionCard({ 
  icon, 
  title, 
  description, 
  iconBgColor, 
  iconColor, 
  onClick 
}: ActionCardProps) {
  
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onClick();
  };

  return (
    <div 
      className="bg-dark-secondary border border-border-primary shadow-lg hover:scale-105 transition-transform cursor-pointer rounded-lg p-4"
      onClick={handleClick}
    >
      <div className="flex items-center space-x-3">
        <div className={`p-2 ${iconBgColor} rounded-lg`}>
          <div className={`w-6 h-6 ${iconColor}`}>
            {icon}
          </div>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-text-primary">{title}</h3>
          <p className="text-sm text-text-tertiary">{description}</p>
        </div>
        <svg 
          className="w-5 h-5 text-text-tertiary" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M9 5l7 7-7 7" 
          />
        </svg>
      </div>
    </div>
  );
}
