import { getDifferentialFrame } from '../services/pipelineApi'
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { sleep } from '../services/api'


export function useHome( {startingWaveLenght, finalWaveLenght} ) {
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
            alert("Upload both videos before analyzing them!")
            return
        }

        setLoading(true)
        const formData = new FormData()
        formData.append('video_prima', videoPrima)
        formData.append('video_dopo', videoDopo)

        try {
            await api.post('/pipeline/', formData)
            setAnalysisReady(true)
            setResponse("Analysis completed successfully.")
            await sleep(1000);
            navigate(`/differential-view/${startingWaveLenght}/${finalWaveLenght}/0`)
        } catch (err) {
            setResponse('Error: ' + err.message)
        } finally {
            setLoading(false)
        }
    }

    async function getFrame(frame = 0) {
        const url = await getDifferentialFrame(frame)
        if (prevDiffUrl.current)
            URL.revokeObjectURL(prevDiffUrl.current)
        prevDiffUrl.current = url
        setUrlDiff(url)
    }

    useEffect(() => {
        if (analysisReady) getFrame(0)
    }, [analysisReady])

    useEffect(() => {
        return () => {
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current)
        }
    }, [])

    return {
        loading,
        response,
        videoPrima, setVideoPrima,
        videoDopo, setVideoDopo,
        analyze
    }
}