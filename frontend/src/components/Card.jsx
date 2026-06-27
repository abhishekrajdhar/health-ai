import React from 'react'

export default function Card({ title, icon: Icon, iconColor = 'text-clinical-600', children, className = '', action }) {
  return (
    <div className={`card animate-fade-in ${className}`}>
      {title && (
        <div className="card-header">
          {Icon && (
            <span className={`flex-shrink-0 ${iconColor}`}>
              <Icon size={16} strokeWidth={2.5} />
            </span>
          )}
          <h3 className="card-title">{title}</h3>
          {action && <div className="ml-auto">{action}</div>}
        </div>
      )}
      {children}
    </div>
  )
}
