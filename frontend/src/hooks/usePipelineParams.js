import { useState, useEffect, useRef } from 'react';
import { runPipeline, getStepOfARoi } from '../services/pipelineApi';
import DEFAULT_PIPELINE_PARAMS from '../constants/DefaultPipelineParams';
import { PIPELINE_STEPS_NUMBER } from '../constants/PipelineStepsNumber';


const DEBOUNCE_MS = 400;

async function urlRetrieverStadiumBased(stadium, roiNumber, params) {
    const url = await Promise.all(
                    Array.from({ length: PIPELINE_STEPS_NUMBER }, (_, i) =>
                        getStepOfARoi(roiNumber, i, params, stadium)
                    )
                );

    return url;
}

export function usePipelineParams(roiNumber) {

    const [params, setParams] = useState(DEFAULT_PIPELINE_PARAMS);
    const [newFirstStepUrl, setNewFirstStepUrl] = useState([]);
    const [newSecondStepUrl, setNewSecondStepUrl] = useState([]);
    const [isNewLoading, setIsNewLoaging] = useState(false);
    const timerRef = useRef(null);

    useEffect(() => {

        if (roiNumber == null)
            return;

        clearTimeout(timerRef.current);

        timerRef.current = setTimeout(async () => {
            setIsNewLoaging(true);

            try {

                const firstUrls = await urlRetrieverStadiumBased("prima", roiNumber, params);
                const secondUrls = await urlRetrieverStadiumBased("dopo", roiNumber, params); 

                setNewFirstStepUrl(firstUrls);
                setNewSecondStepUrl(secondUrls);


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
        newFirstStepUrl, 
        newSecondStepUrl,
        isNewLoading 
    };

}