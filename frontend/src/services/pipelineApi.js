import { BASE_URL } from '../constants/BaseUrl';
import { fetchImage } from './api';

export async function getDifferentialFrame(frame) {
  console.log("Frame Number Required: " + frame);
  if(frame < 0)
    return null;
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



export async function runPipeline(roiNumber) {
  const response = await fetch(`${BASE_URL}/pipeline/roi/prima/${roiNumber}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
}


export async function getStepOfARoi(roiNumber, stepNumber) {
  return await fetchImage(`${BASE_URL}/pipeline/roi/prima/${roiNumber}/step/${stepNumber}`);
}