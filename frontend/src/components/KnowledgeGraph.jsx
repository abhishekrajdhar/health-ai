import React, { useMemo } from 'react'
import { Share2 } from 'lucide-react'
import Card from './Card.jsx'

const TYPE_STYLE = {
  diagnosis:  { fill: '#dbeafe', stroke: '#3b82f6', text: '#1d4ed8' },
  symptom:    { fill: '#d1fae5', stroke: '#10b981', text: '#065f46' },
  condition:  { fill: '#ede9fe', stroke: '#8b5cf6', text: '#5b21b6' },
  code:       { fill: '#fef3c7', stroke: '#f59e0b', text: '#92400e' },
  default:    { fill: '#f1f5f9', stroke: '#94a3b8', text: '#475569' },
}

function getStyle(type) {
  return TYPE_STYLE[type?.toLowerCase()] || TYPE_STYLE.default
}

export default function KnowledgeGraph({ knowledgeGraph }) {
  const W = 560, H = 340, CX = W / 2, CY = H / 2

  const { nodes: rawNodes = [], edges: rawEdges = [] } = knowledgeGraph || {}

  const layout = useMemo(() => {
    if (rawNodes.length === 0) return { nodes: [], edges: [] }

    // Find the primary diagnosis node (first 'diagnosis' type or first node)
    const centerNode = rawNodes.find(n => n.type === 'diagnosis') || rawNodes[0]
    const peripheral = rawNodes.filter(n => n.id !== centerNode.id)

    const positions = {}
    positions[centerNode.id] = { x: CX, y: CY }

    const R = 120
    peripheral.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / Math.max(peripheral.length, 1) - Math.PI / 2
      positions[n.id] = {
        x: CX + R * Math.cos(angle),
        y: CY + R * Math.sin(angle),
      }
    })

    return {
      nodes: rawNodes.map(n => ({ ...n, ...positions[n.id] })),
      edges: rawEdges,
      positions,
    }
  }, [rawNodes, rawEdges])

  if (rawNodes.length === 0) {
    return (
      <Card title="Knowledge Graph" icon={Share2}>
        <p className="text-sm text-slate-400 italic">No knowledge graph data available.</p>
      </Card>
    )
  }

  return (
    <Card title="Knowledge Graph" icon={Share2}>
      <div className="overflow-x-auto scrollbar-thin">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full rounded-lg bg-slate-50 border border-slate-200"
          style={{ minWidth: '320px', height: '320px' }}
        >
          {/* Edge lines */}
          {layout.edges.map((e, i) => {
            const s = layout.positions?.[e.source]
            const t = layout.positions?.[e.target]
            if (!s || !t) return null
            const mx = (s.x + t.x) / 2
            const my = (s.y + t.y) / 2
            return (
              <g key={i}>
                <line
                  x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                  stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="4 2"
                />
                {e.label && (
                  <text x={mx} y={my - 4} textAnchor="middle" fontSize="9" fill="#94a3b8" fontFamily="Inter, sans-serif">
                    {e.label}
                  </text>
                )}
              </g>
            )
          })}

          {/* Nodes */}
          {layout.nodes.map((n) => {
            const style = getStyle(n.type)
            const isCenter = n.x === CX && n.y === CY
            const r = isCenter ? 42 : 34
            const label = n.label || n.id
            const words = label.split(' ')

            return (
              <g key={n.id} className="cursor-pointer">
                <circle
                  cx={n.x} cy={n.y} r={r}
                  fill={style.fill} stroke={style.stroke}
                  strokeWidth={isCenter ? 2.5 : 1.5}
                  filter={isCenter ? 'drop-shadow(0 2px 4px rgba(0,0,0,0.12))' : undefined}
                />
                {/* Text — wrap to 2 lines */}
                {words.length <= 1 ? (
                  <text
                    x={n.x} y={n.y + 1}
                    textAnchor="middle" dominantBaseline="middle"
                    fontSize={isCenter ? 10 : 9}
                    fontWeight={isCenter ? '700' : '600'}
                    fill={style.text}
                    fontFamily="Inter, sans-serif"
                  >
                    {label.length > 14 ? label.slice(0, 12) + '…' : label}
                  </text>
                ) : (
                  <>
                    <text
                      x={n.x} y={n.y - 5}
                      textAnchor="middle" dominantBaseline="middle"
                      fontSize={isCenter ? 10 : 9}
                      fontWeight={isCenter ? '700' : '600'}
                      fill={style.text}
                      fontFamily="Inter, sans-serif"
                    >
                      {words[0].slice(0, 10)}
                    </text>
                    <text
                      x={n.x} y={n.y + 7}
                      textAnchor="middle" dominantBaseline="middle"
                      fontSize={isCenter ? 9 : 8}
                      fontWeight="500"
                      fill={style.text}
                      fontFamily="Inter, sans-serif"
                    >
                      {words.slice(1).join(' ').slice(0, 12)}
                    </text>
                  </>
                )}
                {/* Type label below */}
                {n.type && (
                  <text
                    x={n.x} y={n.y + r + 11}
                    textAnchor="middle"
                    fontSize="8"
                    fill="#94a3b8"
                    fontFamily="Inter, sans-serif"
                  >
                    {n.type}
                  </text>
                )}
              </g>
            )
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-3">
        {Object.entries(TYPE_STYLE).filter(([k]) => k !== 'default').map(([type, s]) => (
          <div key={type} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full border" style={{ background: s.fill, borderColor: s.stroke }} />
            <span className="text-xs text-slate-500 capitalize">{type}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}
