import { useState, useMemo } from 'react';

export function useVideoUpload() {
    const [videoPrima, setVideoPrima] = useState(null);
    const [videoDopo, setVideoDopo] = useState(null);

    const isBothUploaded = useMemo(() => {
        return !!(videoPrima && videoDopo);
    }, [videoPrima, videoDopo]);

    return {
        videoPrima,
        setVideoPrima,
        videoDopo,
        setVideoDopo,
        isBothUploaded,
    };
}
