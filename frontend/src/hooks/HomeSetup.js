import { getDifferentialFrame } from '../services/pipelineApi'
import { useState, useEffect, useRef, use } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { sleep } from '../services/api'

import { getNumberOfFrames } from '../services/pipelineApi'


const navigateToNext = 
            (startingWaveLenght, finalWaveLenght, numberOfFrames) => navigate(
                                `/differential-view/${startingWaveLenght}/${finalWaveLenght}/${numberOfFrames}/1`
                                              )



export function useHome() {
    const navigate = useNavigate()

    const [loading, setLoading] = useState(false)
    const [response, setResponse] = useState(null)
    const [videoPrima, setVideoPrima] = useState(null)
    const [videoDopo, setVideoDopo] = useState(null)
    const [analysisReady, setAnalysisReady] = useState(false)
    const [urlDiff, setUrlDiff] = useState(null)

    const [firstVideoFrameCount, setFirstVideoFrameCount] = useState(0);
    const [secondVideoFrameCount, setSecondVideoFrameCount] = useState(0);
    const [differentFrameCountError, setDifferentFrameCountError] = useState(false);
    const [totalFrameCount, setTotalFrameCount] = useState(1);

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


            const data = await getNumberOfFrames();
            const framesPrima = data.total_frames_prima;
            const framesDopo = data.total_frames_dopo;

            if (framesPrima !== framesDopo)
                setDifferentFrameCountError(true);

            setFirstVideoFrameCount(framesPrima);
            setSecondVideoFrameCount(framesDopo);

            setTotalFrameCount(Math.min(framesPrima, framesDopo));


            setResponse("Analysis completed successfully.")
            await sleep(1000);

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
        if (analysisReady)
            getFrame(0)
    }, [analysisReady])

    useEffect(() => {
        return () => {
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current)
        }
    }, [])
    

    const navigateToNext = (startingWaveLenght, finalWaveLenght, numberOfFrames) => 
        navigate(`/differential-view/${startingWaveLenght}/${finalWaveLenght}/${numberOfFrames}/1`)

    return {
        loading, response,
        videoPrima, setVideoPrima,
        videoDopo, setVideoDopo,
        analyze,
        firstVideoFrameCount,
        secondVideoFrameCount,
        differentFrameCountError, setDifferentFrameCountError,
        totalFrameCount,
        navigateToNext
    }
}