/* questo serve perché se è nel .exe va a recuperare l'url dato dal backend, altrimenti 
   chiama direttamente la 8000*/
export const BASE_URL = window.__BASE_URL__ ?? "http://localhost:8000";