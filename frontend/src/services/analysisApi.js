import { BASE_URL } from '../constants/BaseUrl'
import { clearTemporaryParametrization } from './temporaryParameters'


/**
 * @description Triggers the reset endpoint on the backend to clear all analysis data,
 * then clears the temporary analysis parametrization stored in memory.
 *
 * @returns {Promise<void>}
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
 * @description Handles a backend export response: throws on HTTP error, returns
 * `{ success: false }` if the export was cancelled by the user, otherwise returns the parsed JSON result.
 *
 * @param {Response} response - The fetch Response object returned from the backend.
 * @returns {Promise<{success: false}|object>} The export result or a cancellation indicator.
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
 * @description Exports a pixel-by-pixel differential analysis of a single frame to CSV.
 *
 * @param {number} frameToExport - The frame index to export.
 * @returns {Promise<{success: false}|object>} The export result or a cancellation indicator.
 */
export async function exportFrameToCSV(frameToExport) {
    const response = await fetch(`${BASE_URL}/analysis/export-csv/diff/frame/${frameToExport}/pixels/`);
    return handleExportResponse(response);
}


/**
 * @description Exports the global differential analysis results filtered by wavelength range to CSV.
 *
 * @param {number} minWavelength - The lower bound of the wavelength range.
 * @param {number} maxWavelength - The upper bound of the wavelength range.
 * @returns {Promise<{success: false}|object>} The export result or a cancellation indicator.
 */
export async function exportGlobalToCSV(minWavelength, maxWavelength) {
    const response = await fetch(`${BASE_URL}/analysis/diff/results/${minWavelength}/${maxWavelength}/`);
    return handleExportResponse(response);
}
