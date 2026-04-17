import { useState, useRef, useEffect } from 'react';
import { getDifferentialFrame } from '../services/pipelineApi';

export function useDifferentialFrame() {
    const [urlDiff, setUrlDiff] = useState(null);
    const prevDiffUrl = useRef(null);

    const getFrame = async (frame = 0) => {
        try {
            const url = await getDifferentialFrame(frame);

            if (prevDiffUrl.current) {
                URL.revokeObjectURL(prevDiffUrl.current);
            }

            prevDiffUrl.current = url;
            setUrlDiff(url);
        } catch (err) {
            console.error("Errore nel caricamento del frame differenziale:", err);
        }
    };

    useEffect(() => {
        return () => {
            if (prevDiffUrl.current) {
                URL.revokeObjectURL(prevDiffUrl.current);
            }
        };
    }, []);

    return {
        urlDiff,
        getFrame,
    };
}