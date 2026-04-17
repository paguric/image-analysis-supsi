import { useNavigate } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react';
import { getDifferentialFrame, getDiffWithContours } from "../services/pipelineApi";
import { getRoiCount } from '../services/roiApi';

import { loadDifferentialImage } from './differentialImageLoader';


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


    async function loadDiffFrame() {
        loadDifferentialImage({
            currentFrame,
            isLoadingFunction: setIsLoading,
            differentialFrameGetter: getDifferentialFrame,
            oldDiffUrl: prevDiffUrl,
            setDifferentialUrl: setUrlDiff,
            showContours: false,
            showContoursToggleFunction: setShowContours,
        });
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


        loadDifferentialImage({
            currentFrame,
            isLoadingFunction: setIsContoursLoading,
            differentialFrameGetter: getDiffWithContours,
            oldDiffUrl: prevContoursUrl,           
            setDifferentialUrl: setUrlDiffContours, 
            showContours: true,                    
            showContoursToggleFunction: setShowContours,
        });
    }

    useEffect(() => {
        if (prevContoursUrl.current) {
            URL.revokeObjectURL(prevContoursUrl.current);
            prevContoursUrl.current = null;
        }
        setShowContours(false);
        setUrlDiffContours(null);
        loadDiffFrame();
    }, [currentFrame]);

    useEffect(() => {
        getRoiCount()
            .then(data => setNumberOfRois(data))
            .catch(err => console.error(err));
    }, []);

    useEffect(() => {
        return () => {
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current);
            if (prevContoursUrl.current)
                URL.revokeObjectURL(prevContoursUrl.current);
        };
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