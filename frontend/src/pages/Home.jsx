import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { sleep } from '../services/api'
import Button from '@mui/material/Button';
import VideoSlot from '../components/VideoSlot'
import ImageSlot from '../components/ImageSlot'
import { getDifferentialFrame } from '../services/pipelineApi'
import { selectClasses } from '@mui/material/Select';

function Home() {
  const navigate = useNavigate()

  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [videoPrima, setVideoPrima] = useState(null)
  const [videoDopo, setVideoDopo] = useState(null)
  const [analysisReady, setAnalysisReady] = useState(false)
  const [urlDiff, setUrlDiff] = useState(null)

  const prevDiffUrl = useRef(null)

  const analyze = async () => {
    if (!videoPrima || !videoDopo) {
      alert("Carica entrambi i video prima di analizzare!")
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('video_prima', videoPrima)
    formData.append('video_dopo', videoDopo)

    try {
      await api.post('/pipeline/', formData)
      setAnalysisReady(true)
      setResponse("Analisi completata con successo.")
      await sleep(1000);
      navigate('/differential-view')
    } catch (err) {
      setResponse('Errore: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  async function getFrame(frame = 0) {
    const url = await getDifferentialFrame(frame)
    if (prevDiffUrl.current) URL.revokeObjectURL(prevDiffUrl.current)
    prevDiffUrl.current = url
    setUrlDiff(url)
  }

  useEffect(() => {
    if (analysisReady) getFrame(0)
  }, [analysisReady])

  useEffect(() => {
    return () => {
      if (prevDiffUrl.current) URL.revokeObjectURL(prevDiffUrl.current)
    }
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-8 py-8 min-h-screen flex flex-col justify-center items-center">
      <h1 className="text-center text-2xl font-bold mb-8">Analisi Video</h1>

      <div className="flex justify-center gap-5 flex-wrap mb-8">
        <VideoSlot
          titolo="Video Prima"
          fileSelezionato={videoPrima}
          setFileSelezionato={setVideoPrima}
        />
        <VideoSlot
          titolo="Video Dopo"
          fileSelezionato={videoDopo}
          setFileSelezionato={setVideoDopo}
        />
      </div>

      {response && <p className="mb-4 text-sm">{response}</p>}

      <div className="p-8 flex flex-col items-center gap-4">
        <Button
          onClick={analyze}
          disabled={loading}
          variant="outlined" aria-label="Basic button group"
        >
          {loading ? "Analisi in corso..." : "Analizza"}
        </Button>
      </div>
    </div>
  )
}

export default Home