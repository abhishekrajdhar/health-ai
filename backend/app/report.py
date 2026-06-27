"""PDF clinical report generation using reportlab (pure-Python, no system deps)."""
from __future__ import annotations

import io
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY = colors.HexColor("#0E7490")  # clinical teal
ACCENT = colors.HexColor("#0F172A")
RISK_COLORS = {
    "High": colors.HexColor("#DC2626"),
    "Medium": colors.HexColor("#D97706"),
    "Low": colors.HexColor("#16A34A"),
}


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("H1c", parent=s["Heading1"], textColor=PRIMARY, fontSize=18, spaceAfter=2))
    s.add(ParagraphStyle("Sub", parent=s["Normal"], textColor=colors.grey, fontSize=9, spaceAfter=8))
    s.add(ParagraphStyle("H2c", parent=s["Heading2"], textColor=ACCENT, fontSize=12, spaceBefore=10, spaceAfter=4))
    s.add(ParagraphStyle("Body", parent=s["Normal"], fontSize=9.5, leading=13, alignment=TA_LEFT))
    s.add(ParagraphStyle("Small", parent=s["Normal"], fontSize=8, textColor=colors.grey))
    return s


def build_pdf(data: Dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        leftMargin=0.8 * inch, rightMargin=0.8 * inch,
        title="Clinical Decision Support Report",
    )
    st = _styles()
    flow = []

    flow.append(Paragraph("Agentic Clinical Decision Support — Report", st["H1c"]))
    mode = data.get("mode", "demo").upper()
    flow.append(Paragraph(
        f"Generated {data.get('created_at', '')} &nbsp;|&nbsp; Engine: {mode} "
        f"({data.get('provider', 'demo')}) &nbsp;|&nbsp; Ref: {data.get('request_id', '')[:8]}",
        st["Sub"],
    ))
    flow.append(HRFlowable(width="100%", color=PRIMARY, thickness=1.2))
    flow.append(Spacer(1, 8))

    # Patient
    ex = data.get("extracted", {})
    demo = ex.get("demographics", {})
    flow.append(Paragraph("Patient", st["H2c"]))
    patient_rows = [
        ["Age / Sex", f"{demo.get('age', '—')} / {demo.get('sex', '—')}"],
        ["Symptoms", ", ".join(ex.get("symptoms", [])) or "—"],
        ["History", ", ".join(ex.get("history", [])) or "—"],
        ["Medications", ", ".join(ex.get("medications", [])) or "—"],
        ["Allergies", ", ".join(ex.get("allergies", [])) or "NKDA"],
    ]
    flow.append(_kv_table(patient_rows))

    # Diagnoses
    flow.append(Paragraph("Differential Diagnoses", st["H2c"]))
    dx_rows = [["#", "Diagnosis", "ICD-10", "Confidence"]]
    for i, d in enumerate(data.get("diagnoses", []), 1):
        dx_rows.append([
            str(i), d["name"], d.get("icd10", ""),
            f"{int(d['confidence'] * 100)}%",
        ])
    flow.append(_grid_table(dx_rows, [0.4 * inch, 3.0 * inch, 1.1 * inch, 1.2 * inch]))

    # Risk
    risk = data.get("risk", {})
    flow.append(Paragraph("Risk Assessment", st["H2c"]))
    rc = RISK_COLORS.get(risk.get("level"), colors.grey)
    risk_tbl = Table(
        [[f"{risk.get('level', '—')}  (score {risk.get('score', '—')})",
          ", ".join(risk.get("factors", [])) or "—"]],
        colWidths=[1.7 * inch, 4.0 * inch],
    )
    risk_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), rc),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    flow.append(risk_tbl)

    # Recommendations
    recs = data.get("recommendations", {})
    flow.append(Paragraph("Recommended Clinical Actions", st["H2c"]))
    rec_rows = [
        ["Labs", ", ".join(recs.get("labs", [])) or "—"],
        ["Imaging", ", ".join(recs.get("imaging", [])) or "—"],
        ["Referral", ", ".join(recs.get("referral", [])) or "—"],
        ["Follow-up", ", ".join(recs.get("followup", [])) or "—"],
        ["Suggested CPT", ", ".join(recs.get("cpt_codes", [])) or "—"],
    ]
    flow.append(_kv_table(rec_rows))

    # Explanation
    flow.append(Paragraph("Clinical Reasoning", st["H2c"]))
    flow.append(Paragraph(data.get("explanation", ""), st["Body"]))

    flags = data.get("uncertainty_flags", [])
    if flags:
        flow.append(Paragraph("Uncertainty &amp; Safety Flags", st["H2c"]))
        for f in flags:
            flow.append(Paragraph(f"&bull; {f}", st["Body"]))

    flow.append(Spacer(1, 14))
    flow.append(HRFlowable(width="100%", color=colors.lightgrey, thickness=0.6))
    flow.append(Paragraph(
        "Decision-support output for licensed clinicians. Not a medical device; "
        "not a substitute for professional judgment. Generated by the Cotiviti "
        "Hackathon Agentic CDS prototype.",
        st["Small"],
    ))

    doc.build(flow)
    return buf.getvalue()


def _kv_table(rows):
    t = Table([[Paragraph(f"<b>{k}</b>", _styles()["Body"]), Paragraph(v, _styles()["Body"])]
               for k, v in rows], colWidths=[1.4 * inch, 4.5 * inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _grid_table(rows, col_widths):
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t
