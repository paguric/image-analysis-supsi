import ControlPanel from '../components/ControlPanel';
import { ImgBox } from '../components/ImgBox';
import { useParams, useNavigate } from 'react-router-dom';
import { useSingleRoiView } from '../hooks/SingleRoiViewSetup';
import ImageGrid from '../components/ImageGrid';
import CircularIndeterminate from '../components/CircularIndeterminate';
import { useHandleFrameChange } from '../hooks/useHandleFrameChange';
import { computeWaveLength } from '../hooks/ComputeActualWaveLen';


import { useSetInfoPopup } from '../hooks/useSetInfoPopup'
import { useHandleRoiChange } from '../hooks/useHandleRoiChange';
import { usePipelineParams } from '../hooks/usePipelineParams';

function SingleRoiView() {

    useSetInfoPopup("single_roi_view_title", "single_roi_view_description")

    const { roiNumber, totalRoiCount, frameNumber, totalFrameCount, startingWaveLenght, finalWaveLenght } = useParams();


    const {
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
        finalWaveLenght,
        totalRoiCount
    });


    const { handleRoiChange } = useHandleRoiChange({
        startingWaveLenght,
        finalWaveLenght,
        frameNumber,
        totalFrameCount,
        totalRoiCount
    });

    const {
        params,
        setParams,
        newFirstStepUrl,
        newSecondStepUrl,
        isNewLoading
    } = usePipelineParams(roiNumber);

    const stepsBefore = newFirstStepUrl.map((url, i) => ({ img: url, title: `Step ${i}` }));
    const stepsAfter = newSecondStepUrl.map((url, i) => ({ img: url, title: `Step ${i}` }));



    const currentWavelength = computeWaveLength(startingWaveLenght, finalWaveLenght,
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
                    actualRoi={roiNumber}
                    onFrameChange={handleFrameChange}
                    onRoiChange={handleRoiChange}
                    onParamsChange={setParams}
                    totalFrameCount={totalFrameCount}
                />

            </div>

            {/* Colonna destra */}
            <div className="w-3/4 p-4 h-full overflow-hidden flex flex-col gap-3">

                {/* Riga superiore */}
                <div className="flex gap-3 flex-1 min-h-0 overflow-hidden">
                    <div className="flex-1 min-w-0 overflow-hidden">
                        {isBeforeLoading ? <CircularIndeterminate /> : <ImgBox src={beforeImgUrl} stepName="Before" zoomable={false} />}
                    </div>
                    <div className="flex-1 min-w-0 overflow-hidden">
                        {isAfterLoading ? <CircularIndeterminate /> : <ImgBox src={afterImgUrl} stepName="After" zoomable={false} />}
                    </div>
                    <div className="flex-1 min-w-0 overflow-hidden">
                        {isDiffLoading ? <CircularIndeterminate /> : <ImgBox src={diffImgUrl} stepName="Differential" zoomable={false} />}
                    </div>
                </div>

                {/* Riga inferiore */}
                <div className="flex gap-3 shrink-0">
                    <div className="flex-1 min-w-0 relative">
                        <ImageGrid items={stepsBefore} title="Current Parametrization applied on the first video" />
                        {isNewLoading && (
                            <div className="absolute inset-0 flex items-center justify-center bg-white/60 dark:bg-gray-900/60 rounded">
                                <CircularIndeterminate />
                            </div>
                        )}
                    </div>

                    <div className="flex-1 min-w-0 relative">
                        <ImageGrid items={stepsAfter} title="Current Parametrization applied on the second video" />
                        {isNewLoading && (
                            <div className="absolute inset-0 flex items-center justify-center bg-white/60 dark:bg-gray-900/60 rounded">
                                <CircularIndeterminate />
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}

export default SingleRoiView;
