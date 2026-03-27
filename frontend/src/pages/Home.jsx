import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import '../css/App.css'
import VideoSlot from '../components/VideoSlot'
import ImageSlot from '../components/ImageSlot'

function Home() {
  const navigate = useNavigate()

  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [videoPrima, setVideoPrima] = useState(null)
  const [videoDopo, setVideoDopo] = useState(null)
  const [urlDiff, setUrlDiff] = useState(null)
  const [urlPrima, setUrlPrima] = useState(null)
  const [urlDopo, setUrlDopo] = useState(null)

  const analyze = async () => {
    if (!videoPrima || !videoDopo) {
      alert("Carica entrambi i video prima di chiamare il backend!");
      return;
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('video_prima', videoPrima)
    formData.append('video_dopo', videoDopo)

    try {
      const res = await api.post('/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setUrlPrima(res.data.video_prima_url + '?t=' + Date.now())
      setUrlDopo(res.data.video_dopo_url + '?t=' + Date.now())
      setResponse("Analisi completata con successo.")
    } catch (err) {
      setResponse('Error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  async function getFrame() {
    const response = await api.get('/diff/100', { responseType: 'blob' })
    const blob = response.data
    const url = URL.createObjectURL(blob)
    setUrlDiff(url)
  }

  useEffect(() => {
    return () => {
      if (urlDiff) URL.revokeObjectURL(urlDiff)
    }
  }, [urlDiff])

  return (
    <>
      <h1>Analisi Video</h1>
      
      <div className="layout-tre-video">
        <VideoSlot 
          titolo="Video Prima" 
          fileSelezionato={videoPrima}
          setFileSelezionato={setVideoPrima}
          videoUrl={urlPrima}
        />
        <VideoSlot 
          titolo="Video Dopo"
          fileSelezionato={videoDopo}
          setFileSelezionato={setVideoDopo}
          videoUrl={urlDopo}
        />
        <ImageSlot img_src={urlDiff} />
      </div>

    
      {/* <div className="card">
        <button onClick={analyze} disabled={loading || !videoPrima || !videoDopo}>
          {loading ? 'Analisi in corso...' : "Invia al Backend per l'analisi"}
        </button>
        {response && <p>Response: <strong>{response}</strong></p>}
      </div> 


      <div className='card'>
        <button onClick={getFrame}>Mostra view differenziale</button>
      </div> */}

      <div className='card'>
        <button onClick={() => navigate('/differential-view')}>
          Vai alla DifferentialView
        </button>
      </div>
    </>
  )
}

export default Home