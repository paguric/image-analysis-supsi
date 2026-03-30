import axios from 'axios';
import { BASE_URL } from './baseUrl';

const api = axios.create({ baseURL: BASE_URL });

export async function fetchImage(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default api;