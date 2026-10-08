const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: payload ? 'POST' : 'GET',
    headers: payload ? { 'Content-Type': 'application/json' } : undefined,
    body: payload ? JSON.stringify(payload) : undefined,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const detail = Array.isArray(error.detail) ? error.detail.map((item) => item.msg).join(', ') : error.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export const submitEmergency = (payload) => request('/emergency-response', payload);
export const getHealth = () => request('/health');
