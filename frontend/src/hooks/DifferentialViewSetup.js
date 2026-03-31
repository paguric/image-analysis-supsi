import { useNavigate } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react';
import { getDifferentialFrame, getNumberOfFrames } from "../services/pipelineApi";
import { getRoiCount } from '../services/roiApi';

export function useDifferentialView() {

    const navigate = useNavigate()

    const [numberOfRois, setNumberOfRois] = useState(0);
    const [frameCount, setFrameCount] = useState(100);
    const [urlDiff, setUrlDiff] = useState(null);
    const [currentFrame, setCurrentFrame] = useState(0);
    const prevDiffUrl = useRef(null);
    const debounceTimer = useRef(null);
    const [isLoading, setIsLoading] = useState(true);

    async function loadDiffFrame(frame) {
        setIsLoading(true);
        try {
            const url = await getDifferentialFrame(frame);
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current);
            prevDiffUrl.current = url;
            setUrlDiff(url);
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        loadDiffFrame(currentFrame);
    }, [currentFrame]);

    useEffect(() => {
        getNumberOfFrames()
            .then(data => setFrameCount(data.total_frames))
            .catch(err => console.error(err));
    }, []);

    useEffect(() => {
        getRoiCount()
            .then(data => setNumberOfRois(data))
            .catch(err => console.error(err));
    }, []);

    useEffect(() => {
        return () => {
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current);
        }
    }, []);


    return {
        navigate,
        numberOfRois,
        frameCount,
        currentFrame, setCurrentFrame,
        urlDiff,           
        debounceTimer,  
        isLoading,
    }

}
