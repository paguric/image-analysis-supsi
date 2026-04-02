import axios from 'axios';
import { BASE_URL } from  '../services/constants'

const api = axios.create({ baseURL: BASE_URL });

export async function fetchImage(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = Array.isArray(err.detail)
      ? err.detail.map(e => `${e.loc?.join(".")} — ${e.msg}`).join(", ")
      : (err.detail ?? `HTTP ${res.status}`);
    throw new Error(detail); 
  }
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default api;
