import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000';

const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000
});

export async function getDashboardSummary(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;

  const response = await api.get('/dashboard/summary', { params });
  return response.data;
}

export async function getDashboardTimeseries(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;

  const response = await api.get('/dashboard/timeseries', { params });
  return response.data;
}

export async function getTrendSuggestions(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;

  const response = await api.get('/trends/suggestions', { params });
  return response.data;
}

export async function getTrafficMetrics(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;

  const response = await api.get('/metrics/traffic', { params });
  return response.data;
}
