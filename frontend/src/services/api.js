const API_BASE = '/api';

// Throw an Error carrying the backend `detail` message when a request fails.
async function ensureOk(res, fallback) {
  if (res.ok) return;
  let message = fallback;
  try {
    const body = await res.json();
    if (typeof body?.detail === 'string') message = body.detail;
    else if (Array.isArray(body?.detail)) message = body.detail.map((d) => d.msg).join('; ');
  } catch {
    // non-JSON body
  }
  const err = new Error(message);
  err.status = res.status;
  throw err;
}

export const detectEntity = async (query) => {
  const res = await fetch(`${API_BASE}/scan/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  await ensureOk(res, 'Detection failed');
  return res.json();
};

export const startScan = async (scanPayload) => {
  const res = await fetch(`${API_BASE}/scan/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scanPayload),
  });
  await ensureOk(res, 'Failed to start scan');
  return res.json();
};

export const stopScan = async (scanId) => {
  const res = await fetch(`${API_BASE}/scan/${scanId}/stop`, {
    method: 'POST',
  });
  await ensureOk(res, 'Failed to stop scan');
  return res.json();
};

export const getScanResults = async (scanId) => {
  const res = await fetch(`${API_BASE}/scan/${scanId}/results`);
  await ensureOk(res, 'Failed to load results');
  return res.json();
};

export const getRecentScans = async () => {
  const res = await fetch(`${API_BASE}/scan/recent/list`);
  if (!res.ok) return [];
  return res.json();
};

export const getModules = async () => {
  const res = await fetch(`${API_BASE}/modules`);
  if (!res.ok) return [];
  return res.json();
};

export const getCases = async () => {
  const res = await fetch(`${API_BASE}/cases`);
  if (!res.ok) return [];
  return res.json();
};

export const createCase = async (caseData) => {
  const res = await fetch(`${API_BASE}/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(caseData),
  });
  await ensureOk(res, 'Failed to create case');
  return res.json();
};

export const updateCase = async (caseId, caseData) => {
  const res = await fetch(`${API_BASE}/cases/${caseId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(caseData),
  });
  await ensureOk(res, 'Failed to update case');
  return res.json();
};

export const deleteCase = async (caseId) => {
  const res = await fetch(`${API_BASE}/cases/${caseId}`, {
    method: 'DELETE',
  });
  await ensureOk(res, 'Failed to delete case');
  return res.json();
};

export const getSettings = async () => {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) return {};
  return res.json();
};

export const updateSettings = async (settings) => {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  await ensureOk(res, 'Failed to save settings');
  return res.json();
};

export const getExportUrl = (scanId, format) => {
  return `${API_BASE}/scan/${scanId}/export/${format}`;
};
