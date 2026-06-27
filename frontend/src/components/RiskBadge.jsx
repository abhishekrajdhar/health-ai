import React from 'react'
import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react'

const config = {
  High:   { bg: 'bg-red-50',    border: 'border-red-200',   text: 'text-red-700',   icon: AlertTriangle, iconColor: 'text-red-500',   bar: 'bg-red-500'   },
  Medium: { bg: 'bg-amber-50',  border: 'border-amber-200', text: 'text-amber-700', icon: AlertCircle,   iconColor: 'text-amber-500', bar: 'bg-amber-500' },
  Low:    { bg: 'bg-emerald-50',border: 'border-emerald-200',text: 'text-emerald-700',icon: CheckCircle, iconColor: 'text-emerald-500',bar: 'bg-emerald-500'},
}

export default function RiskBadge({ level, score, factors = [] }) {
  const c = config[level] || config.Medium
  const Icon = c.icon
  const pct = Math.round((score || 0) * 100)

  return (
    <div className={`rounded-xl border ${c.bg} ${c.border} p-5`}>
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2.5 rounded-lg bg-white shadow-sm ${c.border} border`}>
          <Icon size={22} className={c.iconColor} strokeWidth={2.5} />
        </div>
        <div>
          <div className={`text-2xl font-extrabold ${c.text}`}>{level} Risk</div>
          <div className="text-xs text-slate-500 mt-0.5">Composite risk score: {pct}%</div>
        </div>
        <div className={`ml-auto text-4xl font-black ${c.text} opacity-80`}>{pct}<span className="text-lg font-semibold opacity-60">%</span></div>
      </div>

      {/* Score gauge */}
      <div className="mb-4">
        <div className="h-3 rounded-full bg-white border border-slate-200 overflow-hidden shadow-inner">
          <div
            className={`h-full rounded-full ${c.bar} transition-all duration-1000 ease-out`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {factors.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Risk Factors</div>
          <div className="flex flex-wrap gap-1.5">
            {factors.map((f, i) => (
              <span key={i} className={`chip text-xs font-medium px-2.5 py-0.5 bg-white border ${c.border} ${c.text}`}>
                {f}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
