import { BASE_URL } from './constants';
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


export async function refreshRoiParametrization(roiNumber) {
  return fetchImage(`${BASE_URL}/pipeline/roi/prima/${roiNumber}/`, {
    method: "POST",
  });
}


export async function getStepOfARoi(roiNumber, stepNumber) {
  return await fetchImage(`${BASE_URL}/pipeline/roi/prima/${roiNumber}/step/${stepNumber}`);
}