import { BASE_URL } from './baseUrl';
import { fetchImage } from './api';

async function getGeneralRoi(index, frame, stadium) {
  return fetchImage(`${BASE_URL}/roi/${stadium}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index, frame }),
  });
}

export const getPreprocessedROI  = (index, frame) => getGeneralRoi(index, frame, "prima");
export const getPostprocessedROI = (index, frame) => getGeneralRoi(index, frame, "dopo");
export const getDifferentialROI  = (index, frame) => getGeneralRoi(index, frame, "diff");