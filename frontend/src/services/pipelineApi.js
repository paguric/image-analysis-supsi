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



export async function getDiffWithContours(frame) {
  
  if (frame < 0) {
    return null;
  }
  return fetchImage(`${BASE_URL}/pipeline/diff/${frame}/contours/`);
}