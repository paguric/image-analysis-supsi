import { useState } from 'react'
import api from './api'
import './css/App.css'
import VideoSlot from './components/VideoSlot'

/**
 * @class App 
 * @brief rappresenta il componente principale dell'interfaccia
 */
function App() {
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  
  // @brief conserviamo gli oggetti File da inviare al backend
  const [videoPrima, setVideoPrima] = useState(null)
  const [videoDopo, setVideoDopo] = useState(null)
  
  // @brief stati per contenere gli URL dei tre video restituiti dal backend
  const [urlPrima, setUrlPrima] = useState(null)
  const [urlDopo, setUrlDopo] = useState(null)
  const [urlDifferenziale, setUrlDifferenziale] = useState(null)

  /**
   * @brief esegue l'upload dei file video e attende i risultati
   * @details utilizza FormData per impacchettare i file binari in modo sicuro per il protocollo HTTP
   */
  const callBackend = async () => {
    // @brief controlla che entrambi i video siano stati caricati prima di procedere
    if (!videoPrima || !videoDopo) {
      alert("Carica entrambi i video prima di chiamare il backend!");
      return;
    }

    setLoading(true)
    
    // @brief creazione del payload multipart
    // @details sostituiamo gli spazi con underscore per garantire la compatibilità nel parsing del server
    const formData = new FormData()
    formData.append('video_prima', videoPrima)
    formData.append('video_dopo', videoDopo)

    try {
      const res = await api.post('/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // @brief applicazione dei risultati restituiti
      setUrlPrima(res.data.video_prima_url)
      setUrlDopo(res.data.video_dopo_url)
      setUrlDifferenziale(res.data.video_diff_url)
      
      setResponse("Analisi completata con successo.")
    } catch (err) {
      setResponse('Error: ' + err.message)
    } finally {
      // @brief reset dello stato di caricamento per riabilitare l'interfaccia
      setLoading(false)
    }
  }

  return (
    <>
      <h1>Riproduzione Video</h1>
      
      <div className="layout-tre-video">
        {/* @brief slot di input per il caricamento del file prima */}
        <VideoSlot 
          titolo="Video Prima" 
          fileSelezionato={videoPrima}
          setFileSelezionato={setVideoPrima}
          videoUrl={urlPrima}
        />
        
        {/* @brief slot di input per il caricamento del file dopo */}
        <VideoSlot 
          titolo="Video Dopo"
          fileSelezionato={videoDopo}
          setFileSelezionato={setVideoDopo}
          videoUrl={urlDopo}
        />

        {/* @brief slot di output disabilitato per l'inserimento manuale */}
        <VideoSlot 
          titolo="Video Differenziale" 
          videoUrl={urlDifferenziale}
          solaLettura={true}
        />
      </div>

      <div className="card">
        {/* @brief bottone per avviare il processo */}
        {/* @details il bottone ora controlla le due nuove variabili per abilitarsi solo se entrambe sono presenti */}
        <button onClick={callBackend} disabled={loading || !videoPrima || !videoDopo}>
          {loading ? 'Analisi in corso...' : 'Invia al Backend per l\'analisi'}
        </button>
        {/* @brief renderizza la risposta di errore o di successo se presente */}
        {response && <p>Response: <strong>{response}</strong></p>}
      </div>
    </>
  )
}

export default App