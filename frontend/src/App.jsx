import { useState, useEffect } from 'react'
import api from './api'
import './css/App.css'
import VideoSlot from './components/VideoSlot'
import ImageSlot from './components/ImageSlot'

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
  
  // @brief stati per contenere l'URL del frame differenziale richiesto
  const [urlDiff, setUrlDiff] = useState(null)
  const [urlPrima, setUrlPrima] = useState(null)
  const [urlDopo, setUrlDopo] = useState(null)

  /**
   * @brief esegue l'upload dei file video e attende i risultati
   * @details utilizza FormData per impacchettare i file binari in modo sicuro per il protocollo HTTP
   */
  const analyze = async () => {
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

      setUrlPrima(res.data.video_prima_url + '?t=' + Date.now())
      setUrlDopo(res.data.video_dopo_url + '?t=' + Date.now())

      setResponse("Analisi completata con successo.")
    } catch (err) {
      setResponse('Error: ' + err.message)
    } finally {
      // @brief reset dello stato di caricamento per riabilitare l'interfaccia
      setLoading(false)
    }
  }

  async function getFrame() {
    const response = await api.get('/diff/100', { responseType: 'blob' })
    const blob = response.data
    const url = URL.createObjectURL(blob)
    setUrlDiff(url)
  }

  // pulisce la memoria (il frame differenziale richiesto)
  useEffect(() => {
    return () => {
      if (urlDiff) URL.revokeObjectURL(urlDiff)
    }
  }, [urlDiff])

  return (
    <>
      <h1>Analisi Video</h1>
      
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

        <ImageSlot img_src={urlDiff} />
      </div>

      <div className="card">
        {/* @brief bottone per avviare il processo */}
        {/* @details il bottone ora controlla le due nuove variabili per abilitarsi solo se entrambe sono presenti */}
        <button onClick={analyze} disabled={loading || !videoPrima || !videoDopo}>
          {loading ? 'Analisi in corso...' : 'Invia al Backend per l\'analisi'}
        </button>
        {/* @brief renderizza la risposta di errore o di successo se presente */}
        {response && <p>Response: <strong>{response}</strong></p>}
      </div>

      <div className='card'>
        <button onClick={getFrame}>Mostra frame 100!</button>
      </div>
    </>
  )
}

export default App