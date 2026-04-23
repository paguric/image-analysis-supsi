import { BASE_URL } from '../constants/BaseUrl';
import DEFAULT_PIPELINE_PARAMS from '../constants/DefaultPipelineParams';
import { fetchImage } from './api';


/**
 * @description Fetches the differential frame image for a given frame index.
 * Returns `null` if the frame index is less than 1.
 *
 * @param {number} frame - The 1-based frame index to retrieve.
 * @returns {Promise<string|null>} A temporary object URL for the image, or `null`.
 */
export async function getDifferentialFrame(frame) {

  if (frame < 1) {
    return null;
  }

  return fetchImage(`${BASE_URL}/pipeline/diff/${frame - 1}/`);
}


/**
 * @description Fetches the total number of frames of the uploaded video from the backend.
 *
 * @returns {Promise<number>} The total frame count.
 */
export async function getNumberOfFrames() {

  const response = await fetch(`${BASE_URL}/pipeline/get-number-of-frames`);

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}


/**
 * @description Triggers a recomputation of a ROI for the given stadium using new pipeline parameters.
 * Skips the request and returns `undefined` if `params` are identical to the default pipeline params.
 *
 * @param {"prima"|"dopo"} stadium - The processing stage to recompute.
 * @param {number} roiNumber - The index of the ROI to recompute.
 * @param {object} params - The new pipeline parameters to apply.
 * @returns {Promise<object|undefined>} The backend analysis result, or `undefined` if skipped.
 */
export async function getNewComputedRoi(stadium, roiNumber, params)  {

  if (JSON.stringify(params) === JSON.stringify(DEFAULT_PIPELINE_PARAMS)) {
    console.log("Parametri uguali, refresh non chiamato");
    return
  }

  console.log(`invocato ricalcolo roi ${roiNumber} per la fase ${stadium}
                con nuovi parametri: ${JSON.stringify(params)}`);

  const response = await fetch(`${BASE_URL}/pipeline/roi/${stadium}/${roiNumber}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
    });

    if (!response.ok)
      throw new Error(`analyzeRoi ${stadium} failed: ${response.status}`);

    return response.json();
}


/**
 * @description Fetches the image produced by a specific pipeline step for a given ROI.
 * Merges the provided custom parameters over the default pipeline params before sending.
 *
 * @param {number} roiNumber - The index of the ROI.
 * @param {number} stepNumber - The pipeline step index to retrieve.
 * @param {object} [customParams={}] - Partial pipeline parameters to override the defaults.
 * @param {"prima"|"dopo"} stadium - The processing stage (before or after).
 * @returns {Promise<string>} A temporary object URL for the step image.
 */
export async function getStepOfARoi(roiNumber, stepNumber, customParams = {}, stadium) {

  const paramsToSend = {
    ...DEFAULT_PIPELINE_PARAMS,
    ...customParams
  };

  return await fetchImage(`${BASE_URL}/pipeline/roi/${stadium}/${roiNumber}/step/${stepNumber}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(paramsToSend),
  });
}


/**
 * @description Fetches the differential frame image with contour overlays for a given frame index.
 * Returns `null` if the frame index is less than 0.
 *
 * @param {number} frame - The 0-based frame index to retrieve.
 * @returns {Promise<string|null>} A temporary object URL for the image, or `null`.
 */
export async function getDiffWithContours(frame) {

  if (frame < 0) {
    return null;
  }
  return fetchImage(`${BASE_URL}/pipeline/diff/${frame}/contours/`);
}
