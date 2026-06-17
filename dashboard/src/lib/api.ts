const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export function getWSUrl(path: string) {
  return `${WS_BASE}${path}`;
}

export const api = {
  getGridState: () => fetchAPI('/api/grid/state'),
  getMetrics: () => fetchAPI('/api/grid/metrics'),
  getTopology: () => fetchAPI('/api/grid/topology'),
  getVulnerabilities: () => fetchAPI('/api/grid/vulnerabilities'),
  getScenarios: () => fetchAPI('/api/scenarios'),
  runSimulation: (key: string, custom?: string) => {
    const params = new URLSearchParams({ scenario_key: key });
    if (custom) params.append('custom_description', custom);
    return fetchAPI(`/api/simulation/run?${params}`, { method: 'POST' });
  },
  triggerAnalysis: () => fetchAPI('/api/agents/analyze', { method: 'POST' }),
  getAgentLog: () => fetchAPI('/api/agents/log'),
  getDebateLog: () => fetchAPI('/api/agents/debate'),
  designFutureGrid: (city: string, year: number, prompt?: string) => {
    const params = new URLSearchParams({ city, target_year: String(year) });
    if (prompt) params.append('prompt', prompt);
    return fetchAPI(`/api/future-grid/design?${params}`, { method: 'POST' });
  },
  getAlerts: () => fetchAPI('/api/alerts'),
  getHistory: () => fetchAPI('/api/simulation/history'),
  getHealth: () => fetchAPI('/api/health'),
};
