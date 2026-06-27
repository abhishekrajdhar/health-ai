# Cotiviti CDS Frontend

Agentic Clinical Decision Support System — React + Vite + TailwindCSS frontend.

## Quick Start

```bash
cd cotiviti-hackathon/frontend
npm install
npm run dev          # http://localhost:5173
```

Backend must be running at `http://localhost:8000`. The Vite dev server proxies `/api` there automatically.

## Build & Preview

```bash
npm run build
npm run preview      # serves the built dist on port 5173
```

## Docker

```bash
docker build -t cotiviti-cds-frontend .
docker run -p 5173:5173 cotiviti-cds-frontend
```

## Stack
- React 18 + Vite 5
- TailwindCSS 3 + PostCSS
- axios (API calls)
- lucide-react (icons)
- recharts (charts, available for use)
