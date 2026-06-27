import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
})

export async function analyzePatient(payload) {
  const { data } = await client.post('/analyze', payload)
  return data
}

export async function fetchSamples() {
  const { data } = await client.get('/samples')
  return data
}

export function getPdfUrl(requestId) {
  return `/api/report/${requestId}/pdf`
}

export function downloadJson(result) {
  const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `cds-report-${result.request_id || 'export'}.json`
  a.click()
  URL.revokeObjectURL(url)
}
