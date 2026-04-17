let savedRoiPrima = null;

export const setTemporaryParametrization = (roiResponse) => {
  savedRoiPrima = roiResponse;
};

export const getTemporaryParametrization = () => savedRoiPrima;

export const clearTemporaryParametrization = () => {
  savedRoiPrima = null;
};