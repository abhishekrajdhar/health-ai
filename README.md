# Cotiviti Hackathon Project

Agentic Clinical Decision Support System built for the Healthcare AI Hackathon.

This project combines a React frontend with a FastAPI backend to turn structured patient information or free-text clinical notes into a multi-agent clinical reasoning report. The system extracts clinical entities, retrieves supporting evidence, proposes likely diagnoses, estimates risk, recommends next steps, and explains its reasoning in a way that is easy to review in the UI.

> This project is for demonstration and decision support only. It is not a medical device and should not be used for clinical decision-making without appropriate validation.

## What The System Does

The application is designed to simulate a small clinical reasoning pipeline:

1. A user enters patient details or a note.
2. The backend runs a six-step agentic workflow.
3. The result is returned as a structured JSON report.
4. The frontend renders the report with cards, timelines, evidence lists, risk badges, and a knowledge graph.
5. The user can export the result as JSON or PDF.

The project supports both:

- `demo` mode, which runs fully offline with deterministic logic
- `live` mode, which can use LLM providers if API keys are present

## Key Features

- Multi-agent clinical reasoning pipeline
- Structured parsing of symptoms, history, medications, allergies, and demographics
- Evidence retrieval with fallback retrieval backends
- Differential diagnosis ranking with confidence scores
- Risk stratification with factors and severity level
- Action-oriented recommendations for labs, imaging, referral, and follow-up
- Plain-language explanation and summary
- Knowledge graph visualization for relationships between findings
- PDF and JSON export of reports
- Audit trail for recent analyses

## High-Level Architecture

The application has two main parts:

### Frontend

The frontend is a React application built with Vite and TailwindCSS. It provides:

- a patient intake form
- a reasoning timeline
- result cards for evidence, diagnosis, risk, and recommendations
- an explanation panel
- a knowledge graph view
- export controls for PDF and JSON

### Backend

The backend is a FastAPI service that exposes the clinical API. It is responsible for:

- validating input
- running the reasoning pipeline
- persisting analysis results
- generating PDFs
- returning sample patient cases
- serving graph and audit data

## Reasoning Pipeline

The core workflow is organized into six agents:

1. `Parser`
2. `Retrieval`
3. `Diagnosis`
4. `Risk`
5. `Recommendation`
6. `Explanation`

The orchestrator wires these agents together in order. If LangGraph is available, the pipeline uses it. Otherwise, the app falls back to a sequential runner with the same output shape.

### Pipeline Output

The backend returns a structured response containing:

- extracted entities
- evidence items
- diagnoses
- risk assessment
- recommendations
- explanation
- uncertainty flags
- summary
- reasoning trace
- knowledge graph

This response contract is defined in the backend Pydantic models and is mirrored by the frontend UI components.

## Demo Mode And Live Mode

The system is built to work without external API keys.

### Demo Mode

When no provider keys are configured, the app uses a deterministic offline engine. This keeps the project runnable and predictable for demos and local development.

### Live Mode

If OpenAI or Anthropic credentials are present, the backend can switch into live mode and use the configured provider.

## API Overview

The backend exposes these main routes:

- `GET /api/health` - service and engine status
- `GET /api/samples` - sample patient cases for the UI
- `POST /api/analyze` - run the reasoning pipeline
- `GET /api/analyses` - recent analyses
- `GET /api/graph/{id}` - knowledge graph for a prior analysis
- `GET /api/report/{id}/pdf` - downloadable report

## Frontend Experience

The UI is organized around a few core panels:

- a patient input panel for structured data and notes
- a timeline showing the agent reasoning path
- extracted entity chips
- evidence and diagnosis cards
- a risk assessment section
- recommendation cards
- an explanation and uncertainty panel
- a knowledge graph visualization
- export buttons for PDF and JSON

The visual design is intentionally clean and clinical, with a focus on readability and quick review.

## Data Flow

1. The user submits a patient case from the UI.
2. The frontend sends the payload to the backend `/api/analyze` endpoint.
3. The backend validates the request and runs the pipeline.
4. The result is saved to SQLite as an audit trail entry.
5. The frontend renders the report from the returned response.
6. The user can view historical analyses or export a PDF/JSON report.

## Project Structure

```text
cotiviti-hackathon/
├── backend/
│   ├── app/
│   │   ├── agents/          # parser, retrieval, diagnosis, risk, recommendation, explanation
│   │   ├── rag/             # retrieval backends and clinical corpus helpers
│   │   ├── config.py        # runtime settings
│   │   ├── db.py            # SQLite persistence
│   │   ├── graph.py         # pipeline orchestration
│   │   ├── llm.py           # provider abstraction
│   │   ├── main.py          # FastAPI routes
│   │   ├── mock_engine.py   # deterministic offline behavior
│   │   ├── report.py        # PDF generation
│   │   └── schemas.py       # request and response models
│   ├── data/                # demo samples and clinical data
│   └── requirements*.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # UI panels and cards
│   │   ├── api.js           # backend API client
│   │   └── App.jsx          # main application layout
│   └── package.json
├── docs/
│   └── Research_Report.md
└── render.yaml
```

## Tech Stack

- React 18
- Vite 5
- TailwindCSS 3
- FastAPI
- Pydantic 2
- SQLite
- ReportLab
- axios
- lucide-react
- recharts

## Clinical Output Fields

The response schema includes:

- `extracted`: normalized patient data
- `evidence`: supporting snippets and codes
- `diagnoses`: ranked differential diagnoses
- `risk`: severity level, score, and factors
- `recommendations`: follow-up actions and suggestions
- `explanation`: reasoning summary
- `uncertainty_flags`: caveats or missing information
- `summary`: concise clinical summary
- `reasoning_trace`: step-by-step agent trace
- `knowledge_graph`: nodes and edges representing relationships

## Safety And Scope

The system is intentionally framed as decision support rather than automated diagnosis.

Important constraints:

- It should not replace a clinician.
- It should not be treated as a validated medical device.
- Its outputs should be reviewed by qualified professionals.
- Free-text input may be incomplete, ambiguous, or misleading.



