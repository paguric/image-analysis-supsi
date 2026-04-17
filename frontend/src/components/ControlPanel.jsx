import NumberSpinnerBox from './NumberSpinnerBox';
import ButtonGroupBox from './ControlPanelButtonGroup';
import InfoPopupWindow from '../components/InfoPopupWindow'
import DEFAULT_PIPELINE_PARAMS from '../constants/DefaultPipelineParams'
import TEXT from '../constants/ParamsInfos'
import { useState } from 'react';

function ControlPanel({
    startingWavelength,
    finalWavelength,
    actualFrame = 0,
    actualRoi,
    onFrameChange,
    onRoiChange,
    onParamsChange,
    totalFrameCount

}) {


    const [params, setParams] = useState(DEFAULT_PIPELINE_PARAMS);

    const updateParam = (key) => (value) => {
        onParamsChange?.((prev) => ({ ...prev, [key]: value }));
    };


    return (
        <div className="grid grid-cols-1 gap-6 mt-4">

            { /* Gruppo 0 */}
            <NumberSpinnerBox
                name={`Actual ROI`}
                min={1}
                defaultValue={isNaN(Number(actualRoi)) ? 1 : (Number(actualRoi) + Number(1))}
                step={1}
                onChange={onRoiChange}

            />


            <NumberSpinnerBox
                name={`Actual Frame (max allowed: ${totalFrameCount})`}
                min={0}
                defaultValue={isNaN(Number(actualFrame)) ? 0 : Number(actualFrame)}
                step={1}
                onChange={onFrameChange}
            />





            {/* Gruppo 1 */}
            <div>
                <div className="flex items-center gap-3 mb-3">

                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-mono font-semibold flex-shrink-0">
                        1
                    </span>

                    <h3 className="font-semibold text-lg">High Pass Filter</h3>

                    <span>
                        <InfoPopupWindow title={TEXT.high_pass_filter_title} description={TEXT.high_pass_filter} />
                    </span>
                </div>
                <NumberSpinnerBox
                    name="High Pass Filter Window Size"
                    min={0}
                    defaultValue={DEFAULT_PIPELINE_PARAMS.bg_blur_size}
                    step={1}
                    onChange={updateParam('bg_blur_size')}
                    odd={true}
                />

            </div>

            {/* Gruppo 2 */}
            <div>
                <div className="flex items-center gap-3 mb-3">

                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-mono font-semibold flex-shrink-0">
                        2
                    </span>
                    <h3 className="font-semibold text-lg">Local Contrast</h3>
                    <span>
                        <InfoPopupWindow title={TEXT.clahe_title} description={TEXT.clahe} />
                    </span>
                </div>
                <div className="grid grid-cols-1 gap-4">
                    <NumberSpinnerBox
                        name="Clahe Grid Dimension"
                        min={0}
                        defaultValue={DEFAULT_PIPELINE_PARAMS.clahe_grid_size}
                        step={1}
                        onChange={updateParam('clahe_grid_size')}
                    />
                    <NumberSpinnerBox
                        name="Clahe Local Contrast"
                        min={0}
                        defaultValue={DEFAULT_PIPELINE_PARAMS.clahe_clip_limit}
                        step={1}
                        onChange={updateParam('clahe_clip_limit')}
                    />
                </div>
            </div>


            {/* Gruppo 3 */}
            <div>
                <div className="flex items-center gap-3 mb-3">

                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-mono font-semibold flex-shrink-0">
                        3
                    </span>
                    <h3 className="font-semibold text-lg">Canny Edge Detection</h3>
                    <span>
                        <InfoPopupWindow title={TEXT.canny_title} description={TEXT.canny} />
                    </span>
                </div>
                <div className="grid grid-cols-1 gap-4">
                    <NumberSpinnerBox
                        name="Canny Low Threshold"
                        min={0}
                        defaultValue={DEFAULT_PIPELINE_PARAMS.canny_low}
                        step={1}
                        onChange={updateParam('canny_low')}
                    />
                    <NumberSpinnerBox
                        name="Canny High Threshold"
                        min={0}
                        defaultValue={DEFAULT_PIPELINE_PARAMS.canny_high}
                        step={1}
                        onChange={updateParam('canny_high')}
                    />
                </div>
            </div>

            {/* Gruppo 4 */}

            <div>
                <div className="flex items-center gap-3 mb-3">

                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-mono font-semibold flex-shrink-0">
                        4
                    </span>
                    <h3 className="font-semibold text-lg">Morphological Transformation</h3>
                    <span>
                        <InfoPopupWindow title={TEXT.morphological_title} description={TEXT.morphological} />
                    </span>
                </div>
                <div className="grid grid-cols-1 gap-4">
                    <NumberSpinnerBox
                        name="Morph Transformation Window Size"
                        min={0}
                        defaultValue={DEFAULT_PIPELINE_PARAMS.morph_kernel_size}
                        step={1}
                        onChange={updateParam('morph_kernel_size')}
                        odd={true}
                    />
                    <NumberSpinnerBox
                        name="Morph Transformation Number of Iterations"
                        min={0}
                        defaultValue={DEFAULT_PIPELINE_PARAMS.morph_iterations}
                        step={1}
                        onChange={updateParam('morph_iterations')}
                    />
                </div>
            </div>





            {/* Button Group */}
            <div className="mt-6">
                <ButtonGroupBox
                    abortAndNavigateTo={`/differential-view/${startingWavelength}/${finalWavelength}/${totalFrameCount}/${actualFrame}`}
                    saveAndNavigateTo={`/differential-view/${startingWavelength}/${finalWavelength}/${totalFrameCount}/${actualFrame}`}
                />
            </div>

        </div>
    );
}

export default ControlPanel;