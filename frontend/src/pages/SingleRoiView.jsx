import ControlPanel from '../components/ControlPanel';
import { ImgBox } from '../components/ImgBox';
import { useParams, useNavigate } from 'react-router-dom';
import { useSingleRoiView } from '../hooks/SingleRoiViewSetup';
import ImageGrid from '../components/ImageGrid';
import CircularIndeterminate from '../components/CircularIndeterminate';
import { useHandleFrameChange } from '../hooks/useHandleFrameChange';
import { computeWaveLength } from '../hooks/ComputeActualWaveLen';

import { useSetInfoPopup } from '../hooks/useSetInfoPopup'

function SingleRoiView() {

    useSetInfoPopup("single_roi_view_title", "single_roi_view_description") 

    const { roiNumber, frameNumber, totalFrameCount, startingWaveLenght, finalWaveLenght } = useParams();


    const {
        stepUrls,
        isLoading,
        isBeforeLoading,
        isAfterLoading,
        isDiffLoading,
        beforeImgUrl,
        afterImgUrl,
        diffImgUrl
    } = useSingleRoiView(roiNumber, frameNumber);


    const { handleFrameChange } = useHandleFrameChange({
        roiNumber,
        startingWaveLenght,
        totalFrameCount,
        finalWaveLenght
    });

    const stepsBefore = stepUrls.map((url, i) => ({ img: url, title: `Step ${i}` }));
    const stepsAfter = stepUrls.map((url, i) => ({ img: url, title: `Step ${i}` }));


    const currentWavelength = computeWaveLength(    startingWaveLenght, finalWaveLenght,
                                                    frameNumber, totalFrameCount
                                                );

    return (
        <div className="flex h-screen w-full overflow-hidden">

            {/* Colonna sinistra */}
            <div className="w-1/4 p-6 border-r dark:border-gray-700 overflow-y-auto">
                <div className="mb-6">
                    <p className="text-center font-bold text-3xl mb-1 dark:text-gray-100">
                        ROI #{Number(roiNumber) + Number(1)}
                        </p>
                    <p className="text-center text-gray-600 dark:text-gray-400">
                        Current Wavelength: <strong>{isNaN(currentWavelength) ? '-' : `${Number(currentWavelength).toFixed(2)} nm`}</strong>
                    </p>
                </div>

                <ControlPanel
                    startingWavelength={startingWaveLenght}
                    finalWavelength={finalWaveLenght}
                    actualFrame={frameNumber}
                    onFrameChange={handleFrameChange}
                    totalFrameCount={totalFrameCount}
                />

            </div>

            {/* Colonna destra */}
            <div className="w-3/4 p-4 h-full overflow-hidden flex flex-col gap-3">

                {/* Riga superiore */}
                <div className="flex gap-3 flex-1 min-h-0 overflow-hidden">
                    <div className="flex-1 min-w-0 overflow-hidden">
                        {isBeforeLoading ? <CircularIndeterminate /> : <ImgBox src={beforeImgUrl} stepName="Before" />}
                    </div>
                    <div className="flex-1 min-w-0 overflow-hidden">
                        {isAfterLoading ? <CircularIndeterminate /> : <ImgBox src={afterImgUrl} stepName="After" />}
                    </div>
                    <div className="flex-1 min-w-0 overflow-hidden">
                        {isDiffLoading ? <CircularIndeterminate /> : <ImgBox src={diffImgUrl} stepName="Differential" />}
                    </div>
                </div>

                {/* Riga inferiore */}
                <div className="flex gap-3 shrink-0">
                    <div className="flex-1 min-w-0">
                        {/* {isLoading ? <CircularIndeterminate /> : <ImageGrid items={stepsBefore} />} */}
                        <ImgBox src="../../img/placeholder.png" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <ImgBox src="../../img/placeholder.png" />
                    </div>
                </div>

            </div>
        </div>
    );
}

export default SingleRoiView;
