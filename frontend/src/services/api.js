import axios from 'axios';
import { BASE_URL } from  '../constants/BaseUrl'


/**
 * @description Crea un collegamento con il backend
 */
const api = axios.create({ baseURL: BASE_URL });


/**
 * @description Function that manages the images retrieved from the backend 
 * @param {*} url The URL to the backend method endpoint
 * @param {*} options 
 * @returns Restituisce in url per utilizzare l'immagine
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
 * @description This function allows to wait a certaing amount of time before executing the next line 
 * @param {*} ms The amount of time you want to wait (in milliseconds)
 */
export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default api;
