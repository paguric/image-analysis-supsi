import { BASE_URL } from  '../constants/BaseUrl'


export async function clearDataBase() {
    const response = await fetch(`${BASE_URL}/analysis/reset/`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`)
    }
}

// da finire
export function exportToCSV(path) {
    const response = fetch(`${BASE_URL}/analysis/diff/results/`);

    if(!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    return true;
}