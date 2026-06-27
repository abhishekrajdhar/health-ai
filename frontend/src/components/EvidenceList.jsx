import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import Card from './Card.jsx'
import Badge from './Badge.jsx'
import ProgressBar from './ProgressBar.jsx'

function EvidenceItem({ item, index }) {
  const [expanded, setExpanded] = useState(index === 0)
  const score = item.score || 0
  const scoreColor = score >= 0.8 ? 'bg-emerald-500' : score >= 0.6 ? 'bg-amber-500' : 'bg-slate-400'

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
      >
        <div className="w-7 h-7 rounded-full bg-clinical-100 text-clinical-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
          {index + 1}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm text-slate-800 truncate">{item.source}</div>
          <div className="mt-1">
            <ProgressBar value={score} color={scoreColor} showPct={true} height="h-1.5" />
          </div>
        </div>
        <div className="flex items-center gap-2 ml-2">
          <span className="text-xs font-bold text-slate-600">{Math.round(score * 100)}%</span>
          {expanded ? <ChevronUp size={14} className="text-slate-400" /> : <ChevronDown size={14} className="text-slate-400" />}
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-slate-100 bg-slate-50/50">
          <p className="text-sm text-slate-600 leading-relaxed mt-3 mb-3 italic">
            &ldquo;{item.snippet}&rdquo;
          </p>
          <div className="flex flex-wrap gap-1.5">
            {(item.icd_codes || []).map((c, i) => (
              <Badge key={i} variant="blue" size="xs">ICD: {c}</Badge>
            ))}
            {(item.cpt_codes || []).map((c, i) => (
              <Badge key={i} variant="teal" size="xs">CPT: {c}</Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function EvidenceList({ evidence = [] }) {
  return (
    <Card title="Retrieved Clinical Evidence" icon={BookOpen}>
      {evidence.length === 0 ? (
        <p className="text-sm text-slate-400 italic">No evidence retrieved.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {evidence.map((item, i) => (
            <EvidenceItem key={i} item={item} index={i} />
          ))}
        </div>
      )}
    </Card>
  )
}
