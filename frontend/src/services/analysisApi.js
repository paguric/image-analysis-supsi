import { BASE_URL } from  '../constants/BaseUrl'


export async function clearDataBase() {
    console.log("clear database called");
    const response = await fetch(`${BASE_URL}/analysis/reset/`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`)
    }
}