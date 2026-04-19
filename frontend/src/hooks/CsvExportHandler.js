import { exportFrameToCSV, exportGlobalToCSV } from "../services/analysisApi";


const runExport = async (fetcher) => {
    try {
        const result = await fetcher();
        if (result.success) {
            alert(`File successfully exported in: ${result.path}`);
        }
    } catch (err) {
        alert(`Error occurred while saving, please retry`);
    }
};


export const handleFrameExport = (currentFrame) =>
    runExport(() => exportFrameToCSV(currentFrame));


export const handleGlobalExport = (minWavelength, maxWavelength) =>
    runExport(() => exportGlobalToCSV(minWavelength, maxWavelength));
