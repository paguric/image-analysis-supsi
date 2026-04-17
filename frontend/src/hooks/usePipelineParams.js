import { useState, useEffect, useRef } from 'react';
import { getStepOfARoi } from '../services/pipelineApi';
import DEFAULT_PIPELINE_PARAMS from '../constants/DefaultPipelineParams';
import { PIPELINE_STEPS_NUMBER } from '../constants/PipelineStepsNumber';
import { getNewComputedRoi } from '../services/pipelineApi';

const DEBOUNCE_MS = 400;

async function urlRetrieverStadiumBased(stadium, roiNumber, params, isNewLoadingFunction) {
    
    isNewLoadingFunction(true);

    const url = await Promise.all(
                    Array.from({ length: PIPELINE_STEPS_NUMBER }, (_, i) =>
                        getStepOfARoi(roiNumber, i, params, stadium)
                    )
                );

        isNewLoadingFunction(false);

    return url;
}

async function getNewAnalyzedRoi(stadium, roiNumber, params, isNewLoadingFunction) {

    isNewLoadingFunction(true);
    const newImage = await getNewComputedRoi(stadium, roiNumber, params);;
    isNewLoadingFunction(false);

    return newImage; 

}

export function usePipelineParams(roiNumber) {

    const [params, setParams] = useState(DEFAULT_PIPELINE_PARAMS);
    const [newFirstStepUrl, setNewFirstStepUrl] = useState([]);
    const [newSecondStepUrl, setNewSecondStepUrl] = useState([]);
    const [newFirtImage, setNewFirstImage] = useState(null);
    const [newSecondImage, setNewSecondImage] = useState(null);
    const [isNewLoading, setIsNewLoaging] = useState(false);
    const [isNewFirstLoading, setIsNewFirstLoading] = useState(false);
    const [isNewSecondLoading, setIsNewSecondLoading] = useState(false);
    const timerRef = useRef(null);

    useEffect(() => {

        if (roiNumber == null)
            return;

        clearTimeout(timerRef.current);

        timerRef.current = setTimeout(async () => {

            try {


                const firstUrls = await urlRetrieverStadiumBased("prima", roiNumber, params, setIsNewLoaging);
                const secondUrls = await urlRetrieverStadiumBased("dopo", roiNumber, params, setIsNewLoaging); 

                setNewFirstStepUrl(firstUrls);
                setNewSecondStepUrl(secondUrls);


                const firstImageNewAnalysis = await getNewAnalyzedRoi("prima", roiNumber, params, setIsNewFirstLoading);
                const secondImageNewAnalysis = await getNewAnalyzedRoi("dopo", roiNumber, params, setIsNewSecondLoading);

                setNewFirstImage(firstImageNewAnalysis);
                setNewSecondImage(secondImageNewAnalysis);
                


            } catch (err) {
                console.log('Pipeline params fetch failed:', err);
            } finally {
                setIsNewLoaging(false);
                setIsNewFirstLoading(false);
                setIsNewSecondLoading(false);
            }

        }, DEBOUNCE_MS);


        return () => clearTimeout(timerRef.current);

    }, [roiNumber, params])

    
    return {
        params, 
        setParams, 
        newFirstStepUrl, 
        newSecondStepUrl,
        isNewLoading,
        newFirtImage,
        newSecondImage,
        isNewFirstLoading,
        isNewSecondLoading
    };

}