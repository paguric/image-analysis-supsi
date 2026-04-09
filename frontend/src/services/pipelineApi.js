import { BASE_URL } from '../constants/BaseUrl';
import DEFAULT_PIPELINE_PARAMS from '../constants/DefaultPipelineParams';
import { fetchImage } from './api';

export async function getDifferentialFrame(frame) {
  if (frame < 1) {
    return null;
  }
  return fetchImage(`${BASE_URL}/pipeline/diff/${frame - 1}/`);
}

export async function getNumberOfFrames() {
  const response = await fetch(`${BASE_URL}/pipeline/get-number-of-frames`);
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }
  return await response.json();
}

/**
 * Esegue la pipeline su una specifica ROI e restituisce la RoiResponse.
 * Utilizza i parametri di default se non vengono forniti override.
 */
export async function runPipeline(roiNumber, customParams = {}) {
  const paramsToSend = {
    ...DEFAULT_PIPELINE_PARAMS,
    ...customParams
  };

  const response = await fetch(`${BASE_URL}/pipeline/roi/prima/${roiNumber}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(paramsToSend),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(`Failed to run pipeline (HTTP ${response.status}): ${errorText}`);
  }

  return await response.json();
}





export async function getStepOfARoi(roiNumber, stepNumber, customParams = {}) {
  const paramsToSend = {
    ...DEFAULT_PIPELINE_PARAMS,
    ...customParams
  };

  return await fetchImage(`${BASE_URL}/pipeline/roi/prima/${roiNumber}/step/${stepNumber}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(paramsToSend),
  });
}





export async function getDiffWithContours(frame) {
  if (frame < 0) {
    return null;
  }
  return fetchImage(`${BASE_URL}/pipeline/diff/${frame}/contours/`);
}