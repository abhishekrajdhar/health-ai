import React from 'react'
import { Activity, Heart } from 'lucide-react'
import Badge from './Badge.jsx'

export default function Header({ mode }) {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-4">
        {/* Logo mark */}
        <div className="flex items-center gap-2.5 flex-shrink-0">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-clinical-600 to-teal-500 flex items-center justify-center shadow-sm">
            <Activity size={18} color="white" strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-sm leading-tight tracking-tight">
              Agentic Clinical Decision Support
            </div>
            <div className="text-xs text-slate-500 leading-tight">
              Intelligent Diagnostics &amp; Clinical Intelligence Platform
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="hidden md:block h-8 w-px bg-slate-200 mx-1" />

        {/* Cotiviti branding */}
        <div className="hidden md:flex items-center gap-1.5">
          <div className="w-5 h-5 rounded bg-clinical-600 flex items-center justify-center">
            <Heart size={10} color="white" fill="white" />
          </div>
          <span className="text-xs font-semibold text-clinical-700 tracking-wide uppercase">Cotiviti</span>
          <span className="text-xs text-slate-400">Hackathon 2025</span>
        </div>

        <div className="ml-auto flex items-center gap-3">
          {mode && (
            <Badge variant={mode === 'live' ? 'live' : 'demo'} size="sm">
              {mode === 'live' ? '● LIVE' : '◐ DEMO MODE'}
            </Badge>
          )}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            System Online
          </div>
        </div>
      </div>
    </header>
  )
}
