import { BASE_URL } from './baseUrl';
import { fetchImage } from './api';

export async function getDifferentialFrame(frame) {
  return fetchImage(`${BASE_URL}/pipeline/diff/${frame}/`);
}