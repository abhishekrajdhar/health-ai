import React from 'react'
import { FlaskConical, Scan, UserCheck, CalendarClock, Tag } from 'lucide-react'
import Card from './Card.jsx'
import Badge from './Badge.jsx'

function RecSection({ label, items = [], icon: Icon, iconBg, iconColor, emptyMsg }) {
  return (
    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-8 h-8 rounded-lg ${iconBg} flex items-center justify-center`}>
          <Icon size={15} className={iconColor} strokeWidth={2.5} />
        </div>
        <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{label}</span>
      </div>
      {items.length === 0 ? (
        <p className="text-xs text-slate-400 italic">{emptyMsg || 'None indicated'}</p>
      ) : (
        <ul className="flex flex-col gap-1.5">
          {items.map((item, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-slate-700">
              <span className="w-1.5 h-1.5 rounded-full bg-clinical-400 flex-shrink-0" />
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function RecommendationGrid({ recommendations }) {
  if (!recommendations) return null
  const { labs = [], imaging = [], referral = [], followup = [], cpt_codes = [] } = recommendations

  return (
    <Card title="Clinical Recommendations" icon={Tag}>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <RecSection
          label="Laboratory Tests"
          items={labs}
          icon={FlaskConical}
          iconBg="bg-clinical-100"
          iconColor="text-clinical-600"
        />
        <RecSection
          label="Imaging / Diagnostics"
          items={imaging}
          icon={Scan}
          iconBg="bg-teal-100"
          iconColor="text-teal-600"
        />
        <RecSection
          label="Specialist Referral"
          items={referral}
          icon={UserCheck}
          iconBg="bg-purple-100"
          iconColor="text-purple-600"
        />
        <RecSection
          label="Follow-up / Disposition"
          items={followup}
          icon={CalendarClock}
          iconBg="bg-amber-100"
          iconColor="text-amber-600"
        />
      </div>

      {cpt_codes.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">CPT Codes</div>
          <div className="flex flex-wrap gap-1.5">
            {cpt_codes.map((c, i) => (
              <Badge key={i} variant="teal" size="xs">CPT: {c}</Badge>
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}
