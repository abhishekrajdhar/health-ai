import React from 'react'
import { Activity, Brain, Shield, FileText, ArrowLeft } from 'lucide-react'

const features = [
  { icon: Brain,    title: 'Multi-Agent Reasoning',    desc: 'Six specialized AI agents collaborate — from note parsing to clinical explanation.' },
  { icon: Shield,   title: 'Risk Stratification',      desc: 'Composite risk scoring with explainable factors for High / Medium / Low triage.' },
  { icon: FileText, title: 'Evidence-Based Guidance',  desc: 'Recommendations grounded in ACC/AHA, UpToDate, and USPSTF guidelines.' },
  { icon: Activity, title: 'ICD-10 & CPT Mapping',     desc: 'Differential diagnoses and recommendations automatically mapped to billing codes.' },
]

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 animate-fade-in">
      {/* Hero icon */}
      <div className="relative mb-8">
        <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-clinical-500 to-teal-500 flex items-center justify-center shadow-xl">
          <Activity size={44} color="white" strokeWidth={2} />
        </div>
        <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-emerald-400 flex items-center justify-center shadow-md">
          <Brain size={14} color="white" strokeWidth={2.5} />
        </div>
      </div>

      <h2 className="text-2xl font-bold text-slate-800 mb-2 text-center">
        Agentic Clinical Decision Support
      </h2>
      <p className="text-slate-500 text-center max-w-md mb-2">
        Enter patient data in the panel above and click <strong>Analyze Patient</strong> to run the full AI pipeline.
      </p>
      <div className="flex items-center gap-1.5 text-clinical-600 text-sm font-medium mb-10">
        <ArrowLeft size={14} />
        Start with a sample patient
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl">
        {features.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="bg-white border border-slate-200 rounded-xl p-4 shadow-card hover:shadow-card-md transition-shadow">
            <div className="flex items-center gap-2.5 mb-2">
              <div className="w-8 h-8 rounded-lg bg-clinical-100 flex items-center justify-center">
                <Icon size={15} className="text-clinical-600" strokeWidth={2.5} />
              </div>
              <span className="text-sm font-semibold text-slate-800">{title}</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      <div className="mt-10 flex items-center gap-2 text-xs text-slate-400">
        <div className="w-1.5 h-1.5 rounded-full bg-clinical-400" />
        Powered by multi-agent AI &mdash; Cotiviti Hackathon 2025
        <div className="w-1.5 h-1.5 rounded-full bg-teal-400" />
      </div>
    </div>
  )
}
