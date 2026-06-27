import React from 'react'
import { User, Stethoscope, ClipboardList, Pill, AlertOctagon } from 'lucide-react'
import Card from './Card.jsx'
import Badge from './Badge.jsx'

function Section({ label, items = [], variant, icon: Icon, iconColor }) {
  if (!items || items.length === 0) return null
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-2">
        <Icon size={13} className={iconColor} strokeWidth={2.5} />
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{label}</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item, i) => (
          <Badge key={i} variant={variant}>{item}</Badge>
        ))}
      </div>
    </div>
  )
}

export default function EntityChips({ extracted }) {
  if (!extracted) return null
  const { demographics, symptoms, history, medications, allergies } = extracted

  return (
    <Card title="Extracted Medical Entities" icon={ClipboardList}>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {demographics && (
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <User size={13} className="text-clinical-500" strokeWidth={2.5} />
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Demographics</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {demographics.age && <Badge variant="blue">Age {demographics.age}</Badge>}
              {demographics.sex && <Badge variant="blue">{demographics.sex}</Badge>}
            </div>
          </div>
        )}
        <Section label="Symptoms"    items={symptoms}    variant="teal"   icon={Stethoscope} iconColor="text-teal-500" />
        <Section label="History"     items={history}     variant="purple" icon={ClipboardList} iconColor="text-purple-500" />
        <Section label="Medications" items={medications} variant="slate"  icon={Pill}         iconColor="text-slate-500" />
        <Section label="Allergies"   items={allergies}   variant="red"    icon={AlertOctagon}  iconColor="text-red-500" />
      </div>
    </Card>
  )
}
