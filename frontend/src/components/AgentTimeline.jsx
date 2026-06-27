import React from 'react'
import { CheckCircle, Loader, Circle, AlertCircle } from 'lucide-react'

const AGENT_ORDER = [
  'Clinical Note Parser',
  'Knowledge Retrieval',
  'Diagnostic Reasoning',
  'Risk Prediction',
  'Clinical Recommendation',
  'Explanation',
]

const AGENT_ICONS = {
  'Clinical Note Parser':      '📋',
  'Knowledge Retrieval':       '🔍',
  'Diagnostic Reasoning':      '🧠',
  'Risk Prediction':           '📊',
  'Clinical Recommendation':   '💊',
  'Explanation':               '💬',
}

function StatusIcon({ status }) {
  if (status === 'complete')  return <CheckCircle size={16} className="text-emerald-500" strokeWidth={2.5} />
  if (status === 'running')   return <Loader size={16} className="text-clinical-500 animate-spin" strokeWidth={2.5} />
  if (status === 'error')     return <AlertCircle size={16} className="text-red-500" strokeWidth={2.5} />
  return <Circle size={16} className="text-slate-300" strokeWidth={2} />
}

export default function AgentTimeline({ trace = [], isLoading = false }) {
  // Build a map from trace data
  const traceMap = {}
  trace.forEach(t => { traceMap[t.agent] = t })

  // Determine active agent index during loading
  const completedCount = trace.filter(t => t.status === 'complete').length

  return (
    <div className="flex flex-col gap-0">
      {AGENT_ORDER.map((agentName, idx) => {
        const t = traceMap[agentName]
        const status = t ? t.status : (isLoading && idx === completedCount ? 'running' : t ? t.status : 'pending')
        const isLast = idx === AGENT_ORDER.length - 1

        return (
          <div key={agentName} className="flex gap-3">
            {/* Connector line */}
            <div className="flex flex-col items-center">
              <div className={`mt-1 flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center border-2 transition-colors duration-300 ${
                status === 'complete' ? 'bg-emerald-50 border-emerald-400' :
                status === 'running'  ? 'bg-clinical-50 border-clinical-400' :
                status === 'error'    ? 'bg-red-50 border-red-400' :
                'bg-slate-50 border-slate-200'
              }`}>
                <StatusIcon status={status} />
              </div>
              {!isLast && (
                <div className={`w-0.5 flex-1 my-1 rounded-full transition-colors duration-500 ${
                  status === 'complete' ? 'bg-emerald-300' : 'bg-slate-200'
                }`} style={{ minHeight: '16px' }} />
              )}
            </div>

            {/* Content */}
            <div className={`pb-4 flex-1 ${isLast ? '' : ''}`}>
              <div className="flex items-start gap-2 flex-wrap">
                <span className="text-base leading-7">{AGENT_ICONS[agentName]}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-sm font-semibold leading-7 ${
                      status === 'complete' ? 'text-slate-800' :
                      status === 'running'  ? 'text-clinical-700' :
                      'text-slate-400'
                    }`}>{agentName}</span>
                    {status === 'complete' && t?.duration_ms && (
                      <span className="text-xs text-slate-400 font-mono bg-slate-50 px-1.5 py-0.5 rounded">
                        {t.duration_ms}ms
                      </span>
                    )}
                    {status === 'running' && (
                      <span className="text-xs text-clinical-600 font-medium animate-pulse">Processing…</span>
                    )}
                  </div>
                  {t?.detail && (
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{t.detail}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
