import React from 'react'
import { Microscope, Star } from 'lucide-react'
import Card from './Card.jsx'
import Badge from './Badge.jsx'
import ProgressBar from './ProgressBar.jsx'

function confidenceColor(conf) {
  if (conf >= 0.85) return { bar: 'bg-red-500',     text: 'text-red-600',     bg: 'bg-red-50',     border: 'border-red-200' }
  if (conf >= 0.65) return { bar: 'bg-amber-500',   text: 'text-amber-600',   bg: 'bg-amber-50',   border: 'border-amber-200' }
  return              { bar: 'bg-emerald-500', text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200' }
}

export default function DiagnosisList({ diagnoses = [] }) {
  const sorted = [...diagnoses].sort((a, b) => b.confidence - a.confidence)
  const top = sorted[0]
  const rest = sorted.slice(1)

  return (
    <Card title="Differential Diagnoses" icon={Microscope}>
      {sorted.length === 0 ? (
        <p className="text-sm text-slate-400 italic">No diagnoses generated.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {/* Top diagnosis */}
          {top && (() => {
            const c = confidenceColor(top.confidence)
            return (
              <div className={`rounded-xl border-2 ${c.border} ${c.bg} p-4`}>
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-white rounded-lg shadow-sm flex-shrink-0">
                    <Star size={16} className={c.text} fill="currentColor" strokeWidth={0} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-slate-900 text-base">{top.name}</span>
                      <Badge variant="outline" size="xs">{top.icd10}</Badge>
                      <span className={`ml-auto text-2xl font-black ${c.text}`}>
                        {Math.round(top.confidence * 100)}<span className="text-sm font-semibold opacity-70">%</span>
                      </span>
                    </div>
                    <div className="mt-2">
                      <ProgressBar value={top.confidence} color={c.bar} showPct={false} height="h-2.5" />
                    </div>
                    {top.rationale && (
                      <p className="mt-2 text-xs text-slate-600 leading-relaxed">{top.rationale}</p>
                    )}
                  </div>
                </div>
              </div>
            )
          })()}

          {/* Remaining */}
          {rest.map((dx, i) => {
            const c = confidenceColor(dx.confidence)
            return (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-white hover:bg-slate-50/70 transition-colors">
                <div className="w-6 h-6 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                  {i + 2}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-sm text-slate-800">{dx.name}</span>
                    <Badge variant="outline" size="xs">{dx.icd10}</Badge>
                    <span className={`ml-auto text-sm font-bold ${c.text}`}>
                      {Math.round(dx.confidence * 100)}%
                    </span>
                  </div>
                  <div className="mt-1.5">
                    <ProgressBar value={dx.confidence} color={c.bar} showPct={false} height="h-1.5" />
                  </div>
                  {dx.rationale && (
                    <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">{dx.rationale}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
