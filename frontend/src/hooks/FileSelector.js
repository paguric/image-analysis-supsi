export async function useFileSelector(suggestedName = 'output.csv') {

  // Caso PyWebView (sviluppo locale con pywebview o .exe)
  if (window.pywebview?.api?.save_file_dialog) {
    const path = await window.pywebview.api.save_file_dialog(suggestedName);
    return path ?? null;
  } 

  // Fallback browser: chiedi solo il nome file, il backend decide dove salvare
  // oppure mostra un input testuale
  const name = window.prompt('Nome del file di output:', suggestedName);
  return name ?? null;
}
