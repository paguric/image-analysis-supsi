import { BASE_URL } from  '../constants/BaseUrl'
import { fetchImage } from './api';
import { getTemporaryParametrization } from './temporaryParameters'


async function getGeneralRoi(index, frame, stadium) {

  console.log(`RICHIESTA ROI ${index} ${stadium}`);

  return fetchImage(`${BASE_URL}/roi/${stadium}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index, frame }),
  });
}

export const getPreprocessedROI  = (index, frame) => getGeneralRoi(index, frame, "prima");
export const getPostprocessedROI = (index, frame) => getGeneralRoi(index, frame, "dopo");
export const getDifferentialROI  = (index, frame) => getGeneralRoi(index, frame, "diff");


export async function getRoiCount() {
  const response = await fetch(`${BASE_URL}/roi/number-of-rois`)

  if(!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}


export async function saveRoiParametrization() {

  const informationsToSend = getTemporaryParametrization();

  const response = await fetch(`${BASE_URL}/roi/save/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(informationsToSend)
  });

  if(!response.ok)
    throw new Error(`Error while saving ${response.status}`);

  return true;

}