import { BASE_URL } from '../constants/BaseUrl'
import { clearTemporaryParametrization } from './temporaryParameters'


/**
 * @description This function triggers the clear database function
 * in the backend and the clear of the temporary analysis parametrization.
 */
export async function clearDataBase() {
    const response = await fetch(`${BASE_URL}/analysis/reset/`, {
        method: 'DELETE',
    });

    clearTemporaryParametrization();

    if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`)
    }
}

/**
 * @description Function to handle the csv export response 
 * @param {*} response takes the response returned from the backend call
 * @returns returns the analyzed result from the backend call
 */
async function handleExportResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    const result = await response.json();

    if (result.cancelled) {
        console.log("Export annullato dall'utente");
        return { success: false };
    }

    return result;
}

/**
 * @description Function to handle the pixel-by-pixel, single frame CSV export
 * @param {*} frameToExport takes as parameter the frame you want to export
 * @returns returns the analyzed result from the backend call
 */
export async function exportFrameToCSV(frameToExport) {
    const response = await fetch(`${BASE_URL}/analysis/export-csv/diff/frame/${frameToExport}/pixels/`);
    return handleExportResponse(response);
}


/**
 * @description Function to handle the global CSV export
 * @param {*} minWavelength the starting wavelength
 * @param {*} maxWavelength the final wavelength
 * @returns returns the analyzed result from the backend call
 */
export async function exportGlobalToCSV(minWavelength, maxWavelength) {
    const response = await fetch(`${BASE_URL}/analysis/diff/results/${minWavelength}/${maxWavelength}/`);
    return handleExportResponse(response);
}
