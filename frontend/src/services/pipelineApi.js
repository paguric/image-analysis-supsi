import { BASE_URL } from './baseUrl';
import { fetchImage } from './api';

export async function getDifferentialFrame(frame) {
  return fetchImage(`${BASE_URL}/pipeline/diff/${frame}/`);
}


export async function getNumberOfFrames() {
  const response = await fetch(`${BASE_URL}/pipeline/get-number-of-frames`);
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }
  const data = await response.json();
  return data;
}