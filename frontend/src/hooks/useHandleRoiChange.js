import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export function useHandleRoiChange({ startingWaveLenght, finalWaveLenght, frameNumber, totalFrameCount, totalRoiCount }) {
    const navigate = useNavigate();
    const debounceTimer = useRef(null);

    const total = Number(totalRoiCount);
    const frame = Number(frameNumber);
    const frames = Number(totalFrameCount);

    const handleRoiChange = (newRoi) => {
        if (debounceTimer.current) clearTimeout(debounceTimer.current);

        const clampedRoi = Math.min(Number(newRoi), total) - 1;

        debounceTimer.current = setTimeout(() => {
            navigate(
                `/single-roi-view/${clampedRoi}/${total}/${frame}/${frames}/${startingWaveLenght}/${finalWaveLenght}`,
                { replace: true }
            );
        }, 180);
    };

    return { handleRoiChange };
}