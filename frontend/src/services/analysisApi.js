import { BASE_URL } from '../constants/BaseUrl'
import { clearTemporaryParametrization } from './temporaryParameters'


export async function clearDataBase() {
    const response = await fetch(`${BASE_URL}/analysis/reset/`, {
        method: 'DELETE',
    });

    clearTemporaryParametrization();

    if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`)
    }
}


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


export async function exportFrameToCSV(frameToExport) {
    const response = await fetch(`${BASE_URL}/analysis/export-csv/diff/frame/${frameToExport}/pixels/`);
    return handleExportResponse(response);
}


export async function exportGlobalToCSV(minWavelength, maxWavelength) {
    const response = await fetch(`${BASE_URL}/analysis/diff/results/${minWavelength}/${maxWavelength}/`);
    return handleExportResponse(response);
}
