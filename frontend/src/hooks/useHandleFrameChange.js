import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export function useHandleFrameChange({ roiNumber, startingWaveLenght, finalWaveLenght, totalFrameCount, totalRoiCount }) {
    const navigate = useNavigate();
    const debounceTimer = useRef(null);

    const handleFrameChange = (newFrame) => {
        if (debounceTimer.current) clearTimeout(debounceTimer.current);

        const clampedFrame = Math.min(Number(newFrame), Number(totalFrameCount));

        debounceTimer.current = setTimeout(() => {
            navigate(
                `/single-roi-view/${roiNumber}/${totalRoiCount}/${clampedFrame - 1}/${totalFrameCount}/${startingWaveLenght}/${finalWaveLenght}`,
                { replace: true }
            );
        }, 180);
    };

    return { handleFrameChange };
}