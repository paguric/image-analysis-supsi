import { BASE_URL } from  '../constants/BaseUrl'
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


export async function exportToCSV() {
  const response = await fetch(`${BASE_URL}/analysis/export-csv/`);
  
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  const result = await response.json();
  
  if (result.cancelled) {
    console.log("Export annullato dall'utente");
    return { success: false };
  }
  
  return result; // { success: true, path: "/home/user/export.csv" }
}