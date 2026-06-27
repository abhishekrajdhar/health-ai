import React from 'react'

export default function ProgressBar({ value, max = 1, color = 'bg-clinical-500', label, showPct = true, height = 'h-2' }) {
  const pct = Math.round((value / max) * 100)
  return (
    <div className="w-full">
      {(label || showPct) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-xs text-slate-500">{label}</span>}
          {showPct && <span className="text-xs font-semibold text-slate-700">{pct}%</span>}
        </div>
      )}
      <div className={`progress-bar ${height}`}>
        <div
          className={`progress-fill ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
