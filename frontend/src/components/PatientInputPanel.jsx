import React, { useState, useEffect } from 'react'
import { UserCircle, Loader, ChevronDown, X, Plus, RotateCcw, Zap } from 'lucide-react'
import Card from './Card.jsx'
import { fetchSamples } from '../api.js'

function ChipInput({ label, placeholder, value, onChange }) {
  const [input, setInput] = useState('')

  function addChip(raw) {
    const items = raw.split(/[,\n]+/).map(s => s.trim()).filter(Boolean)
    if (items.length) onChange([...value, ...items])
    setInput('')
  }

  function handleKey(e) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addChip(input)
    }
  }

  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">{label}</label>
      <div className="min-h-[42px] rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 flex flex-wrap gap-1.5 focus-within:ring-2 focus-within:ring-clinical-500 focus-within:border-transparent transition-all">
        {value.map((chip, i) => (
          <span key={i} className="inline-flex items-center gap-1 bg-clinical-100 text-clinical-700 text-xs font-medium px-2 py-0.5 rounded-full">
            {chip}
            <button onClick={() => onChange(value.filter((_, j) => j !== i))} className="hover:text-clinical-900">
              <X size={10} strokeWidth={3} />
            </button>
          </span>
        ))}
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          onBlur={() => input.trim() && addChip(input)}
          placeholder={value.length === 0 ? placeholder : '+ add more…'}
          className="flex-1 min-w-[120px] text-sm outline-none bg-transparent text-slate-800 placeholder-slate-400 py-0.5"
        />
      </div>
      <p className="text-xs text-slate-400 mt-1">Press Enter or comma to add</p>
    </div>
  )
}

const AGENT_STEPS = [
  'Clinical Note Parser',
  'Knowledge Retrieval',
  'Diagnostic Reasoning',
  'Risk Prediction',
  'Clinical Recommendation',
  'Explanation',
]

export default function PatientInputPanel({ onAnalyze, isLoading }) {
  const [age, setAge] = useState('')
  const [sex, setSex] = useState('')
  const [symptoms, setSymptoms] = useState([])
  const [history, setHistory] = useState([])
  const [medications, setMedications] = useState([])
  const [allergies, setAllergies] = useState([])
  const [note, setNote] = useState('')
  const [samples, setSamples] = useState([])
  const [step, setStep] = useState(0)

  useEffect(() => {
    fetchSamples()
      .then(setSamples)
      .catch(() => setSamples([]))
  }, [])

  // Animate stepper during loading
  useEffect(() => {
    if (!isLoading) { setStep(0); return }
    setStep(0)
    let current = 0
    const id = setInterval(() => {
      current += 1
      if (current >= AGENT_STEPS.length) { clearInterval(id); return }
      setStep(current)
    }, 900)
    return () => clearInterval(id)
  }, [isLoading])

  function loadSample(idx) {
    const s = samples[idx]
    if (!s) return
    setAge(s.age || '')
    setSex(s.sex || '')
    setSymptoms(s.symptoms || [])
    setHistory(s.history || [])
    setMedications(s.medications || [])
    setAllergies(s.allergies || [])
    setNote(s.note || '')
  }

  function clear() {
    setAge(''); setSex(''); setSymptoms([]); setHistory([])
    setMedications([]); setAllergies([]); setNote('')
  }

  function handleSubmit(e) {
    e.preventDefault()
    const payload = {}
    if (age)              payload.age = Number(age)
    if (sex)              payload.sex = sex
    if (symptoms.length)  payload.symptoms = symptoms
    if (history.length)   payload.history = history
    if (medications.length) payload.medications = medications
    if (allergies.length) payload.allergies = allergies
    if (note.trim())      payload.note = note.trim()
    onAnalyze(payload)
  }

  return (
    <Card title="Patient Input" icon={UserCircle}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Sample loader */}
        {samples.length > 0 && (
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <select
                defaultValue=""
                onChange={e => { if (e.target.value !== '') loadSample(Number(e.target.value)) }}
                className="input-base appearance-none pr-8 text-slate-600"
              >
                <option value="" disabled>Load sample patient…</option>
                {samples.map((s, i) => (
                  <option key={i} value={i}>{s.name || `Sample ${i + 1}`}</option>
                ))}
              </select>
              <ChevronDown size={14} className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            </div>
          </div>
        )}

        {/* Demographics row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">Age</label>
            <input
              type="number" min="0" max="130"
              value={age} onChange={e => setAge(e.target.value)}
              placeholder="e.g. 62"
              className="input-base"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">Sex</label>
            <div className="relative">
              <select value={sex} onChange={e => setSex(e.target.value)} className="input-base appearance-none pr-8">
                <option value="">Select…</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
              <ChevronDown size={14} className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            </div>
          </div>
        </div>

        <ChipInput label="Symptoms"    placeholder="e.g. Chest pain, Shortness of breath…" value={symptoms}    onChange={setSymptoms} />
        <ChipInput label="Medical History" placeholder="e.g. Hypertension, Diabetes…"       value={history}     onChange={setHistory} />
        <ChipInput label="Medications" placeholder="e.g. Metformin 500mg…"                   value={medications} onChange={setMedications} />
        <ChipInput label="Allergies"   placeholder="e.g. Penicillin…"                        value={allergies}   onChange={setAllergies} />

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">
            Clinical Note <span className="text-slate-400 normal-case font-normal">(optional free text)</span>
          </label>
          <textarea
            value={note}
            onChange={e => setNote(e.target.value)}
            rows={4}
            placeholder="Paste or type the clinical note here…"
            className="input-base resize-none font-mono text-xs leading-relaxed"
          />
        </div>

        {/* Agent stepper (visible during loading) */}
        {isLoading && (
          <div className="bg-clinical-50 border border-clinical-200 rounded-xl p-4">
            <div className="text-xs font-semibold text-clinical-700 mb-3 flex items-center gap-2">
              <Loader size={13} className="animate-spin" strokeWidth={2.5} />
              Running 6-agent pipeline…
            </div>
            <div className="flex flex-col gap-2">
              {AGENT_STEPS.map((name, i) => (
                <div key={name} className="flex items-center gap-2.5">
                  <div className={`w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center transition-all duration-300 ${
                    i < step  ? 'bg-emerald-500' :
                    i === step ? 'bg-clinical-500 animate-pulse-slow' :
                    'bg-slate-200'
                  }`}>
                    {i < step ? (
                      <svg viewBox="0 0 12 12" className="w-3 h-3" fill="none">
                        <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    ) : (
                      <span className="text-white text-[9px] font-bold">{i + 1}</span>
                    )}
                  </div>
                  <span className={`text-xs font-medium transition-colors duration-300 ${
                    i < step  ? 'text-emerald-600' :
                    i === step ? 'text-clinical-700' :
                    'text-slate-400'
                  }`}>{name}</span>
                  {i === step && <Loader size={11} className="text-clinical-500 animate-spin ml-auto" strokeWidth={2.5} />}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-1">
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary flex-1 justify-center"
          >
            {isLoading ? (
              <><Loader size={15} className="animate-spin" /> Analyzing…</>
            ) : (
              <><Zap size={15} /> Analyze Patient</>
            )}
          </button>
          <button type="button" onClick={clear} disabled={isLoading} className="btn-secondary">
            <RotateCcw size={14} /> Clear
          </button>
        </div>
      </form>
    </Card>
  )
}
