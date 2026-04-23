import { BASE_URL } from '../constants/BaseUrl'
import { fetchImage } from './api';
import { getTemporaryParametrization } from './temporaryParameters'

/**
 * @description Generic function that fetches a ROI image for a given index, frame and stadium.
 *
 * @param {number} index - Index of the ROI to retrieve.
 * @param {number} frame - Frame number within the video.
 * @param {"prima"|"dopo"|"diff"} stadium - Processing stage: before, after or differential.
 * @param {object|null} [response=null] - Optional pipeline response to attach to the request body.
 * @returns {Promise<string>} A temporary object URL for the ROI image.
 */
async function getGeneralRoi(index, frame, stadium, response = null) {

  console.log(`RICHIESTA ROI ${index} ${stadium}`);

  return fetchImage(`${BASE_URL}/roi/${stadium}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        data: { index, frame },
        response
    }),
  });
}

/**
 * @description Fetches the preprocessed (before) ROI image for a given index and frame.
 *
 * @param {number} index - Index of the ROI.
 * @param {number} frame - Frame number within the video.
 * @param {object|null} [response=null] - Optional pipeline response.
 * @returns {Promise<string>} A temporary object URL for the ROI image.
 */
export const getPreprocessedROI = (index, frame, response = null) => getGeneralRoi(index, frame, "prima", response);

/**
 * @description Fetches the postprocessed (after) ROI image for a given index and frame.
 *
 * @param {number} index - Index of the ROI.
 * @param {number} frame - Frame number within the video.
 * @param {object|null} [response=null] - Optional pipeline response.
 * @returns {Promise<string>} A temporary object URL for the ROI image.
 */
export const getPostprocessedROI = (index, frame, response = null) => getGeneralRoi(index, frame, "dopo", response);

/**
 * @description Fetches the differential ROI image for a given index and frame.
 *
 * @param {number} index - Index of the ROI.
 * @param {number} frame - Frame number within the video.
 * @param {object|null} [response=null] - Optional pipeline response.
 * @returns {Promise<string>} A temporary object URL for the ROI image.
 */
export const getDifferentialROI = (index, frame, response = null) => getGeneralRoi(index, frame, "diff", response);


/**
 * @description Fetches the total number of ROIs stored in the database.
 *
 * @returns {Promise<number>} The total count of ROIs.
 */
export async function getRoiCount() {
  const response = await fetch(`${BASE_URL}/roi/number-of-rois`)

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}


/**
 * @description Saves a single ROI parametrization payload to the backend.
 *
 * @param {object} payload - The ROI parametrization object to persist.
 * @returns {Promise<void>}
 */
async function saveOne(payload) {
  const response = await fetch(`${BASE_URL}/roi/save/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok)
    throw new Error(`Error while saving ${response.status}`);
}


/**
 * @description Saves the current temporary ROI parametrization (before and/or after stages) to the backend.
 * Reads the temporary state via {@link getTemporaryParametrization} and persists
 * whichever stages are defined. Both saves run in parallel via `Promise.all`.
 *
 * @returns {Promise<boolean>} `true` if at least one stage was saved, `false` if nothing to save.
 */
export async function saveRoiParametrization() {

  const { prima, dopo } = getTemporaryParametrization();

  const tasks = [];
  if (prima) tasks.push(saveOne(prima));
  if (dopo) tasks.push(saveOne(dopo));

  if (tasks.length === 0) return false;

  await Promise.all(tasks);
  return true;

}
