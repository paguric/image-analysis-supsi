import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useVideoUpload } from './useVideoUpload';
import { usePipelineAnalysis } from './usePipelineAnalysis';
import { useDifferentialFrame } from './useDifferentialFrame';

export function useHome({ startingWaveLenght, finalWaveLenght }) {
    const navigate = useNavigate();

    const videoUpload = useVideoUpload();
    const analysis = usePipelineAnalysis();
    const differential = useDifferentialFrame();

    useEffect(() => {
        if (analysis.analysisReady) {
            differential.getFrame(0);
        }
    }, [analysis.analysisReady, differential.getFrame]);

    const navigateToNext = (startingWaveLength, finalWaveLength, numberOfFrames) => {
        navigate(`/differential-view/${startingWaveLength}/${finalWaveLength}/${numberOfFrames}/1`);
    };

    // Navigazione automatica quando i frame counts sono uguali (nessun alert da mostrare).
    // Dipende solo da analysis.loading: scatta alla fine dell'analisi, non quando
    // l'utente preme "Abort" (che cambierebbe differentFrameCountError ma non loading).
    useEffect(() => {
        if (analysis.analysisReady && !analysis.loading && !analysis.differentFrameCountError) {
            navigateToNext(startingWaveLenght, finalWaveLenght, analysis.totalFrameCount);
        }
    }, [analysis.loading]); // eslint-disable-line react-hooks/exhaustive-deps

    const handleAnalyze = () => {
        analysis.analyze(videoUpload.videoPrima, videoUpload.videoDopo);
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
        resetAnalysis: analysis.resetAnalysis,

        urlDiff: differential.urlDiff,

        navigateToNext,
    };
}