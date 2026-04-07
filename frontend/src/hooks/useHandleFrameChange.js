import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export function useHandleFrameChange({ roiNumber, startingWaveLenght, finalWaveLenght, frameCount }) {
    const navigate = useNavigate();
    const debounceTimer = useRef(null);

    const handleFrameChange = (newFrame) => {
        if (debounceTimer.current) {
            clearTimeout(debounceTimer.current);
        }

        if (newFrame > frameCount) {
            debounceTimer.current = setTimeout(() => {
                setFrameCountError(true);
                navigate(`/single-roi-view/${roiNumber}/${frameCount}/${startingWaveLenght}/${finalWaveLenght}`, { replace: true });
            }, 180);
            return;  
        }

        debounceTimer.current = setTimeout(() => {
            navigate(`/single-roi-view/${roiNumber}/${newFrame}/${startingWaveLenght}/${finalWaveLenght}`, { replace: true });
        }, 180);
    };

    return { handleFrameChange };
}