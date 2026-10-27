const API_BASE = '/api';

export const detectEntity = async (query) => {
  const res = await fetch(`${API_BASE}/scan/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error('Detection failed');
  return res.json();
};

export const startScan = async (scanPayload) => {
  const res = await fetch(`${API_BASE}/scan/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scanPayload),
  });
  if (!res.ok) throw new Error('Failed to start scan');
  return res.json();
};

export const stopScan = async (scanId) => {
  const res = await fetch(`${API_BASE}/scan/${scanId}/stop`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to stop scan');
  return res.json();
};

export const getScanResults = async (scanId) => {
  const res = await fetch(`${API_BASE}/scan/${scanId}/results`);
  if (!res.ok) throw new Error('Failed to load results');
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
  if (!res.ok) throw new Error('Failed to create case');
  return res.json();
};

export const updateCase = async (caseId, caseData) => {
  const res = await fetch(`${API_BASE}/cases/${caseId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(caseData),
  });
  if (!res.ok) throw new Error('Failed to update case');
  return res.json();
};

export const deleteCase = async (caseId) => {
  const res = await fetch(`${API_BASE}/cases/${caseId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete case');
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
  if (!res.ok) throw new Error('Failed to save settings');
  return res.json();
};

export const getExportUrl = (scanId, format) => {
  return `${API_BASE}/scan/${scanId}/export/${format}`;
};
