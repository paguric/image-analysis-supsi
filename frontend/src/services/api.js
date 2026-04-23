import axios from 'axios';
import { BASE_URL } from  '../constants/BaseUrl'


/**
 * @description Axios instance pre-configured with the application base URL.
 */
const api = axios.create({ baseURL: BASE_URL });


/**
 * @description Fetches a resource from the backend and returns a temporary object URL
 * pointing to the received Blob. Throws a descriptive error if the response is not OK.
 *
 * @param {string} url - The backend endpoint URL.
 * @param {RequestInit} [options={}] - Optional fetch options (method, headers, body, etc.).
 * @returns {Promise<string>} A temporary object URL usable as an image `src`.
 */
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

/**
 * @description Returns a Promise that resolves after the specified number of milliseconds.
 *
 * @param {number} ms - Duration to wait in milliseconds.
 * @returns {Promise<void>}
 */
export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default api;
