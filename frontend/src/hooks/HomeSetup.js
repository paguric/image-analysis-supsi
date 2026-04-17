import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useVideoUpload } from './useVideoUpload';
import { usePipelineAnalysis } from './usePipelineAnalysis';
import { useDifferentialFrame } from './useDifferentialFrame';

export function useHome() {
    const navigate = useNavigate();

    const videoUpload = useVideoUpload();
    const analysis = usePipelineAnalysis();
    const differential = useDifferentialFrame();

    useEffect(() => {
        if (analysis.analysisReady) {
            differential.getFrame(0);
        }
    }, [analysis.analysisReady, differential.getFrame]);

    const handleAnalyze = () => {
        analysis.analyze(videoUpload.videoPrima, videoUpload.videoDopo);
    };

    const navigateToNext = (startingWaveLength, finalWaveLength, numberOfFrames) => {
        navigate(`/differential-view/${startingWaveLength}/${finalWaveLength}/${numberOfFrames}/1`);
    };

    return {
        videoPrima: videoUpload.videoPrima,
        setVideoPrima: videoUpload.setVideoPrima,
        videoDopo: videoUpload.videoDopo,
        setVideoDopo: videoUpload.setVideoDopo,
        isBothUploaded: videoUpload.isBothUploaded,

        loading: analysis.loading,
        response: analysis.response,
        analysisReady: analysis.analysisReady,
        firstVideoFrameCount: analysis.firstVideoFrameCount,
        secondVideoFrameCount: analysis.secondVideoFrameCount,
        differentFrameCountError: analysis.differentFrameCountError,
        setDifferentFrameCountError: analysis.setDifferentFrameCountError,

        totalFrameCount: analysis.totalFrameCount,
        analyze: handleAnalyze,

        urlDiff: differential.urlDiff,

        navigateToNext,
    };
}