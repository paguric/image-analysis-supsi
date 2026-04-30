import { useState } from 'react';
import api, { sleep } from '../services/api';
import { getNumberOfFrames } from '../services/pipelineApi';

export function usePipelineAnalysis() {
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [analysisReady, setAnalysisReady] = useState(false);

    const [firstVideoFrameCount, setFirstVideoFrameCount] = useState(0);
    const [secondVideoFrameCount, setSecondVideoFrameCount] = useState(0);
    const [differentFrameCountError, setDifferentFrameCountError] = useState(false);
    const [totalFrameCount, setTotalFrameCount] = useState(1);

    const analyze = async (videoPrima, videoDopo) => {
        if (!videoPrima || !videoDopo) {
            alert("Upload both videos before analyzing them!");
            return;
        }

        setLoading(true);

        try {
            if (typeof videoPrima === 'string') {
                await api.post('/pipeline/local/', { video_prima: videoPrima, video_dopo: videoDopo });
            } else {
                const formData = new FormData();
                formData.append('video_prima', videoPrima);
                formData.append('video_dopo', videoDopo);
                await api.post('/pipeline/', formData);
            }
            setAnalysisReady(true);

            const data = await getNumberOfFrames();
            const framesPrima = data.total_frames_prima;
            const framesDopo = data.total_frames_dopo;

            if (framesPrima !== framesDopo) {
                setDifferentFrameCountError(true);
            }

            setFirstVideoFrameCount(framesPrima);
            setSecondVideoFrameCount(framesDopo);
            setTotalFrameCount(Math.min(framesPrima, framesDopo));

            setResponse("Analysis completed successfully.");
            await sleep(1000);

        } catch (err) {
            setResponse('Error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    return {
        loading,
        response,
        analysisReady,
        firstVideoFrameCount,
        secondVideoFrameCount,
        differentFrameCountError, setDifferentFrameCountError,
        totalFrameCount,
        analyze,          
    };
}