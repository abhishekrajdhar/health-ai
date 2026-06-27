import React, { useState } from 'react'
import Header from './components/Header.jsx'
import PatientInputPanel from './components/PatientInputPanel.jsx'
import AgentTimeline from './components/AgentTimeline.jsx'
import EntityChips from './components/EntityChips.jsx'
import EvidenceList from './components/EvidenceList.jsx'
import DiagnosisList from './components/DiagnosisList.jsx'
import RiskBadge from './components/RiskBadge.jsx'
import RecommendationGrid from './components/RecommendationGrid.jsx'
import ExplanationCard from './components/ExplanationCard.jsx'
import KnowledgeGraph from './components/KnowledgeGraph.jsx'
import EmptyState from './components/EmptyState.jsx'
import Card from './components/Card.jsx'
import { analyzePatient, getPdfUrl, downloadJson } from './api.js'
import { Download, FileJson, Clock, AlertCircle, Cpu } from 'lucide-react'

export default function App() {
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleAnalyze(payload) {
    setIsLoading(true)
    setError(null)
    try {
      const data = await analyzePatient(payload)
      setResult(data)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'An unexpected error occurred.'
      setError(msg)
    } finally {
      setIsLoading(false)
    }
  }

  const risk = result?.risk || {}
  const hasResult = !!result

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header mode={result?.mode} />

      <main className="max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 flex flex-col gap-6">
        {/* Two-column layout: input left, timeline right */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input panel — wider */}
          <div className="lg:col-span-2">
            <PatientInputPanel onAnalyze={handleAnalyze} isLoading={isLoading} />
          </div>

          {/* Agent timeline */}
          <div>
            <Card
              title="Agent Reasoning Pipeline"
              icon={Cpu}
              className="h-full"
            >
              {!hasResult && !isLoading ? (
                <p className="text-sm text-slate-400 italic">Pipeline will run on analysis.</p>
              ) : (
                <AgentTimeline
                  trace={result?.reasoning_trace || []}
                  isLoading={isLoading}
                />
              )}
            </Card>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 animate-fade-in">
            <AlertCircle size={18} className="text-red-500 flex-shrink-0 mt-0.5" strokeWidth={2.5} />
            <div>
              <div className="font-semibold text-red-700 text-sm">Analysis failed</div>
              <p className="text-sm text-red-600 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Main results area */}
        {!hasResult && !isLoading && !error && (
          <EmptyState />
        )}

        {hasResult && (
          <div className="flex flex-col gap-6 animate-slide-up">
            {/* Request metadata ribbon */}
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 bg-white border border-slate-200 rounded-xl px-4 py-2.5 shadow-card">
              <Clock size={13} strokeWidth={2.5} />
              <span className="font-mono text-slate-600">{result.request_id}</span>
              <span className="hidden sm:block text-slate-300">|</span>
              <span className="hidden sm:block">Mode: <strong className="text-slate-700">{result.mode}</strong></span>
            </div>

            {/* Extracted entities */}
            <EntityChips extracted={result.extracted} />

            {/* Evidence + Diagnoses side by side on large screens */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <EvidenceList evidence={result.evidence} />
              <DiagnosisList diagnoses={result.diagnoses} />
            </div>

            {/* Risk score */}
            <Card title="Risk Assessment" icon={AlertCircle} iconColor="text-red-500">
              <RiskBadge
                level={risk.level}
                score={risk.score}
                factors={risk.factors}
              />
            </Card>

            {/* Recommendations */}
            <RecommendationGrid recommendations={result.recommendations} />

            {/* Explanation + uncertainty */}
            <ExplanationCard
              explanation={result.explanation}
              uncertaintyFlags={result.uncertainty_flags}
              summary={result.summary}
            />

            {/* Knowledge graph */}
            <KnowledgeGraph knowledgeGraph={result.knowledge_graph} />

            {/* Export bar */}
            <div className="flex flex-wrap items-center gap-3 bg-white border border-slate-200 rounded-xl px-5 py-4 shadow-card">
              <span className="text-sm font-semibold text-slate-700">Export Report</span>
              <div className="ml-auto flex gap-2">
                <button
                  onClick={() => window.open(getPdfUrl(result.request_id), '_blank')}
                  className="btn-primary"
                >
                  <Download size={15} /> Export PDF Report
                </button>
                <button
                  onClick={() => downloadJson(result)}
                  className="btn-secondary"
                >
                  <FileJson size={15} /> Export JSON
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-4">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
          <span>Agentic Clinical Decision Support System &mdash; Cotiviti Hackathon 2025</span>
          <span className="text-slate-300">For demonstration purposes only. Not for clinical use.</span>
        </div>
      </footer>
    </div>
  )
}
