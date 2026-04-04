import { useEffect, useState } from 'react';
import { PIPELINE_STEPS_NUMBER } from '../constants/PipelineStepsNumber'
import { getStepOfARoi, runPipeline } from '../services/pipelineApi';
import { getPreprocessedROI, getPostprocessedROI, getDifferentialROI } from '../services/roiApi';
import { getNumberOfFrames } from '../services/pipelineApi';

export function useSingleRoiView(roiNumber, frameNumber) {


    const [stepUrls, setStepUrls] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isBeforeLoading, setIsBeforeLoading] = useState(false);
    const [isAfterLoading, setIsAfterLoading] = useState(false);
    const [isDiffLoading, setIsDiffLoading] = useState(false);
    const [error, setError] = useState(null);

    const [beforeImgUrl, setBeforeImgUrl] = useState(null);
    const [afterImgUrl, setAfterImgUrl] = useState(null);
    const [diffImgUrl, setDiffImgUrl] = useState(null);
    const [frameCount, setFrameCount] = useState(0);

    useEffect(() => {
        getNumberOfFrames()
            .then(data => setFrameCount(data.total_frames))
            .catch(err => console.error(err));
    }, []);



    useEffect(() => {

        async function loadBeforeImg() {

            setIsBeforeLoading(true);
            setError(false);

            try {
                const promise = getPreprocessedROI(roiNumber, frameNumber);
                const url = await promise;

                setBeforeImgUrl(url);

            } catch (err) {
                console.error("Errore nel caricamento degli step:", err);
            } finally {
                setIsBeforeLoading(false);
            }
        }



        async function loadAfterImg() {

            setIsAfterLoading(true);
            setError(false);

            try {
                const promise = getPostprocessedROI(roiNumber, frameNumber);
                const url = await promise;

                setAfterImgUrl(url);

            } catch (err) {
                console.error("Errore nel caricamento degli step:", err);
            } finally {
                setIsAfterLoading(false);
            }
        }


        async function loadDiffImg() {


            setIsDiffLoading(true);
            setError(false);

            try {
                const promise = getDifferentialROI(roiNumber, frameNumber);
                const url = await promise;

                setDiffImgUrl(url);

            } catch (err) {
                console.error("Errore nel caricamento degli step:", err);
            } finally {
                setIsDiffLoading(false);
            }

        }


        async function loadAllSteps() {
            setIsLoading(true);
            setError(false);
            try {
                await runPipeline(roiNumber);

                const promises = [];

                for (let i = 0; i < PIPELINE_STEPS_NUMBER; i++) {
                    promises.push(getStepOfARoi(roiNumber, i));
                }
                
                const urls = await Promise.all(promises);
                setStepUrls(urls);
            } catch (err) {
                console.error("Errore:", err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        }

        loadBeforeImg();
        loadAfterImg();
        loadDiffImg();
        loadAllSteps();

        return () => {
            stepUrls.forEach(url => objectUrlRevoker(url));
            objectUrlRevoker(beforeImgUrl);
            objectUrlRevoker(afterImgUrl);
            objectUrlRevoker(diffImgUrl);
        }

    }, [roiNumber, frameNumber]);


    return {
        stepUrls,
        isLoading,
        isBeforeLoading,
        isAfterLoading,
        isDiffLoading,
        beforeImgUrl,
        afterImgUrl,
        diffImgUrl,
        frameCount
    }
}


function objectUrlRevoker(url) {
    URL.revokeObjectURL(url)
}