let savedRoi = { prima: null, dopo: null };

export const setTemporaryParametrization = (fase, roiResponse) => {
  savedRoi[fase] = roiResponse;
};

export const getTemporaryParametrization = (fase) =>
  fase ? savedRoi[fase] : { ...savedRoi };

export const clearTemporaryParametrization = () => {
  savedRoi = { prima: null, dopo: null };
};
