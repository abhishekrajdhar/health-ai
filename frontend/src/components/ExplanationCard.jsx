import React from 'react'
import { MessageSquare, AlertTriangle } from 'lucide-react'
import Card from './Card.jsx'

export default function ExplanationCard({ explanation, uncertaintyFlags = [], summary }) {
  return (
    <Card title="AI Clinical Reasoning" icon={MessageSquare}>
      {explanation && (
        <div className="mb-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Clinical Explanation</div>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 rounded-lg p-4 border border-slate-200">
            {explanation}
          </p>
        </div>
      )}

      {summary && (
        <div className="mb-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Structured Summary</div>
          <pre className="text-xs text-slate-600 leading-relaxed bg-slate-50 rounded-lg p-4 border border-slate-200 whitespace-pre-wrap font-sans overflow-x-auto scrollbar-thin">
            {summary}
          </pre>
        </div>
      )}

      {uncertaintyFlags.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <AlertTriangle size={13} className="text-amber-500" strokeWidth={2.5} />
            <span className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Uncertainty Flags</span>
          </div>
          <div className="flex flex-col gap-2">
            {uncertaintyFlags.map((flag, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-amber-50 border border-amber-200 rounded-lg p-3">
                <AlertTriangle size={14} className="text-amber-500 flex-shrink-0 mt-0.5" strokeWidth={2.5} />
                <p className="text-xs text-amber-800 leading-relaxed">{flag}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}
