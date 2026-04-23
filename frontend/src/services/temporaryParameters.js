let savedRoi = { prima: null, dopo: null };

/**
 * @description Stores a ROI response for the given processing stage in temporary memory.
 * Overwrites any previously saved value for that stage.
 *
 * @param {"prima"|"dopo"} fase - The processing stage to update.
 * @param {object|null} roiResponse - The ROI response data to store.
 * @returns {void}
 */
export const setTemporaryParametrization = (fase, roiResponse) => {
  savedRoi[fase] = roiResponse;
};

/**
 * @description Returns the temporary ROI parametrization.
 * If `fase` is provided, returns only that stage's data; otherwise returns a shallow copy of both stages.
 *
 * @param {"prima"|"dopo"|undefined} [fase] - The processing stage to retrieve, or omit for all stages.
 * @returns {object|null} The ROI data for the requested stage, or `{ prima, dopo }` for both.
 */
export const getTemporaryParametrization = (fase) =>
  fase ? savedRoi[fase] : { ...savedRoi };

/**
 * @description Resets the temporary ROI parametrization, setting both stages back to `null`.
 *
 * @returns {void}
 */
export const clearTemporaryParametrization = () => {
  savedRoi = { prima: null, dopo: null };
};
