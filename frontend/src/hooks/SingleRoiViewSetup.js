import { useEffect, useState } from 'react';
import { imageLoader } from './imageLoader';

import { getPreprocessedROI, getPostprocessedROI, getDifferentialROI } from '../services/roiApi'


export function useSingleRoiView(roiNumber, frameNumber, primaResponse = null, dopoResponse = null) {

    const [isBeforeLoading, setIsBeforeLoading] = useState(false);
    const [beforeImgUrl, setBeforeImgUrl] = useState(null);

    const [isAfterLoading, setIsAfterLoading] = useState(false);
    const [afterImgUrl, setAfterImgUrl] = useState(null);

    const [isDiffLoading, setIsDiffLoading] = useState(false);
    const [diffImgUrl, setDiffImgUrl] = useState(null);

    const [error, setError] = useState(null);

    useEffect(() => {
        const loadImages = async () => {

            try {
                await Promise.all([
                    imageLoader({
                        setImageLoadingState: setIsBeforeLoading,
                        setError,
                        setImageUrl: setBeforeImgUrl,
                        imageGetter: getPreprocessedROI,
                        roiNumber,
                        frameNumber,
                        response: primaResponse
                    }),

                    imageLoader({
                        setImageLoadingState: setIsAfterLoading,
                        setError,
                        setImageUrl: setAfterImgUrl,
                        imageGetter: getPostprocessedROI,
                        roiNumber,
                        frameNumber,
                        response: dopoResponse
                    }),

                    imageLoader({
                        setImageLoadingState: setIsDiffLoading,
                        setError,
                        setImageUrl: setDiffImgUrl,
                        imageGetter: getDifferentialROI,
                        roiNumber,
                        frameNumber
                    })
                ]);

            } catch (err) {
                console.error("Errore nel caricamento delle immagini:", err);
                setError(err.message || "Errore durante il caricamento");
            }
        };

        loadImages();

        return () => {
            if (beforeImgUrl)  URL.revokeObjectURL(beforeImgUrl);
            if (afterImgUrl)   URL.revokeObjectURL(afterImgUrl);
            if (diffImgUrl)    URL.revokeObjectURL(diffImgUrl);
        };

    }, [roiNumber, frameNumber, primaResponse, dopoResponse]);

    return {
        isBeforeLoading,
        isAfterLoading,
        isDiffLoading,
        beforeImgUrl,
        afterImgUrl,
        diffImgUrl
    };
}
