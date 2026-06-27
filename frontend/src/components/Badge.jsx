import React from 'react'

const variants = {
  blue:    'bg-clinical-100 text-clinical-700 border border-clinical-200',
  teal:    'bg-teal-100 text-teal-700 border border-teal-200',
  green:   'bg-emerald-100 text-emerald-700 border border-emerald-200',
  amber:   'bg-amber-100 text-amber-700 border border-amber-200',
  red:     'bg-red-100 text-red-700 border border-red-200',
  purple:  'bg-purple-100 text-purple-700 border border-purple-200',
  slate:   'bg-slate-100 text-slate-600 border border-slate-200',
  outline: 'bg-white text-slate-600 border border-slate-300',
  demo:    'bg-amber-500 text-white border border-amber-600',
  live:    'bg-emerald-500 text-white border border-emerald-600',
}

export default function Badge({ children, variant = 'slate', size = 'sm', className = '' }) {
  const sz = size === 'xs' ? 'px-1.5 py-0.5 text-xs' : size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-sm'
  return (
    <span className={`chip font-medium ${sz} ${variants[variant] || variants.slate} ${className}`}>
      {children}
    </span>
  )
}
