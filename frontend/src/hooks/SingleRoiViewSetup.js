import { useEffect, useState } from 'react';
import { PIPELINE_STEPS_NUMBER } from '../services/constants';
import { getStepOfARoi } from '../services/pipelineApi';


export function useSingleRoiView(roiNumber) {


    const [stepUrls, setStepUrls] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {

        async function loadAllSteps() {

            setIsLoading(true);
            setError(false);

            try {
                const promises = [];

                for (let i = 0; i <= PIPELINE_STEPS_NUMBER; i++) {
                    promises.push(getStepOfARoi(roiNumber, j));
                }

                const urls = await Promise.all(promises);
                setStepUrls(urls);

            } catch (err) {

            } finally {

                setIsLoading(false);
            }
        }

        loadAllSteps();

        
        useEffect(() => {
            stepUrls.forEach(url => URL.revokeObjectURL(url));
        });

    }, [roiNumber]);


    return {
        stepUrls,
        isLoading,
        error
    }
}