import { useState } from 'react';
import { PIPELINE_STEPS_NUMBER } from '../services/constants';
import { getStepOfARoi } from '../services/pipelineApi';
import { getRoiCount } from '../services/roiApi'


function getAllSteps(stepsForeachRoi) {

    for (let i = 0; i <= getRoiCount(); i++) {

        for(let j = 0; j <= PIPELINE_STEPS_NUMBER; j++) {

            stepsForeachRoi.set((i+1), getStepOfARoi(i, j));

        }
    }
}


export function useSingleRoiView() {


    const [urlBefore, setUrlBefore] = useState(null);
    const [urlAfter, setUrlAfter] = useState(null);
    const [urlDiff, setUrlDiff] = useState(null);
    const [stepList, setStepList] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const debounceTimer = useRef(null);

    const stepsForeachRoi = new Map();

    getAllSteps(stepsForeachRoi);



    

}