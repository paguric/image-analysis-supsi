import { useState, useEffect, useRef } from 'react';
import { runPipeline, getStepOfARoi } from '../services/pipelineApi';
import DEFAULT_PIPELINE_PARAMS from '../constants/DefaultPipelineParams';
import { PIPELINE_STEPS_NUMBER } from '../constants/PipelineStepsNumber';


const DEBOUNCE_MS = 400;

export function usePipelineParams(roiNumber) {

    const [params, setParams] = useState(DEFAULT_PIPELINE_PARAMS);
    const [newStepUrl, setNewStepUrl] = useState([]);
    const [isNewLoading, setIsNewLoaging] = useState(false);
    const timerRef = useRef(null);

    useEffect(() => {

        if (roiNumber == null)
            return;


        clearTimeout(timerRef.current);

        timerRef.current = setTimeout(async () => {
            setIsNewLoaging(true);

            try {

                const urls = await Promise.all(
                    Array.from({ length: PIPELINE_STEPS_NUMBER }, (_, i) =>
                        getStepOfARoi(roiNumber, i, params)
                    )
                );
                setNewStepUrl(urls);
            } catch (err) {
                console.log('Pipeline params fetch failed:', err);
            } finally {
                setIsNewLoaging(false);
            }

        }, DEBOUNCE_MS);


        return () => clearTimeout(timerRef.current);

    }, [roiNumber, params])

    
    return { 
        params, 
        setParams, 
        newStepUrl, 
        isNewLoading 
    };

}