import { useNavigate } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react';
import { getDifferentialFrame, getNumberOfFrames, getDiffWithContours } from "../services/pipelineApi";
import { getRoiCount } from '../services/roiApi';

export function useDifferentialView(actualFrame) {

    const navigate = useNavigate()

    const [numberOfRois, setNumberOfRois] = useState(0);
    const [frameCount, setFrameCount] = useState(100);
    const [urlDiff, setUrlDiff] = useState(null);
    const [currentFrame, setCurrentFrame] = useState(Number(actualFrame) || 1);
    const prevDiffUrl = useRef(null);
    const debounceTimer = useRef(null);
    const [isLoading, setIsLoading] = useState(true);
    const [showContours, setShowContours] = useState(false);
    const [isContoursLoading, setIsContoursLoading] = useState(false);
    const [urlDiffContours, setUrlDiffContours] = useState(null);
    const prevContoursUrl = useRef(null);

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

    async function toggleContours() {
        if (showContours) {
            setShowContours(false);
            return;
        }

        if (urlDiffContours) {
            setShowContours(true);
            return;
        }

        setIsContoursLoading(true);
        try {
            const url = await getDiffWithContours(currentFrame);
            if (prevContoursUrl.current)
                URL.revokeObjectURL(prevContoursUrl.current);
            prevContoursUrl.current = url;
            setUrlDiffContours(url);
            setShowContours(true);
        } catch (err) {
            console.error("Errore nel caricamento dei contorni:", err);
        } finally {
            setIsContoursLoading(false);
        }
    }

    useEffect(() => {
        setShowContours(false);
        setUrlDiffContours(null);
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
        urlDiffContours,
        showContours,
        toggleContours,
        isContoursLoading,
        debounceTimer,
        isLoading,
    }

}
