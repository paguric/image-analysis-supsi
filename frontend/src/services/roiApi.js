import { BASE_URL } from '../constants/BaseUrl'
import { fetchImage } from './api';
import { getTemporaryParametrization } from './temporaryParameters'


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

export const getPreprocessedROI = (index, frame, response = null) => getGeneralRoi(index, frame, "prima", response);
export const getPostprocessedROI = (index, frame, response = null) => getGeneralRoi(index, frame, "dopo", response);
export const getDifferentialROI = (index, frame, response = null) => getGeneralRoi(index, frame, "diff", response);


export async function getRoiCount() {
  const response = await fetch(`${BASE_URL}/roi/number-of-rois`)

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}


async function saveOne(payload) {
  const response = await fetch(`${BASE_URL}/roi/save/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok)
    throw new Error(`Error while saving ${response.status}`);
}


export async function saveRoiParametrization() {

  const { prima, dopo } = getTemporaryParametrization();

  const tasks = [];
  if (prima) tasks.push(saveOne(prima));
  if (dopo) tasks.push(saveOne(dopo));

  if (tasks.length === 0) return false;

  await Promise.all(tasks);
  return true;

}