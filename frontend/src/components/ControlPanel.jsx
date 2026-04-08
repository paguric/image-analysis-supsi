import NumberSpinnerBox from './NumberSpinnerBox';
import ButtonGroupBox from './ControlPanelButtonGroup';

function ControlPanel({
    startingWavelength,
    finalWavelength,
    actualFrame = 0,
    actualRoi,
    onFrameChange,
    onRoiChange,
    totalFrameCount
}) {

    return (
        <div className="grid grid-cols-1 gap-6 mt-4">


            <NumberSpinnerBox
                name={`Actual ROI`}
                min={1}
                defaultValue={isNaN(Number(actualRoi)) ? 1 : Number(actualRoi)}
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
                </div>
                <NumberSpinnerBox
                    name="High Pass Filter Window Size"
                    min={0}
                    defaultValue={101}
                    step={2}
                />
            </div>

            {/* Gruppo 2 */}
            <div>
                <div className="flex items-center gap-3 mb-3">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-mono font-semibold flex-shrink-0">
                        2
                    </span>
                    <h3 className="font-semibold text-lg">Morphological Transformation</h3>
                </div>
                <div className="grid grid-cols-1 gap-4">
                    <NumberSpinnerBox
                        name="Morph Transformation Window Size"
                        min={0}
                        defaultValue={3}
                        step={1}
                    />
                    <NumberSpinnerBox
                        name="Morph Transformation Number of Iterations"
                        min={0}
                        defaultValue={2}
                        step={1}
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
                </div>
                <div className="grid grid-cols-1 gap-4">
                    <NumberSpinnerBox
                        name="Canny Low Threshold"
                        min={0}
                        defaultValue={0}
                        step={1}
                    />
                    <NumberSpinnerBox
                        name="Canny High Threshold"
                        min={0}
                        defaultValue={0}
                        step={1}
                    />
                </div>
            </div>

            {/* Gruppo 4 */}
            <div>
                <div className="flex items-center gap-3 mb-3">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-mono font-semibold flex-shrink-0">
                        4
                    </span>
                    <h3 className="font-semibold text-lg">Acceptance Parameters</h3>
                </div>
                <div className="grid grid-cols-1 gap-4">
                    <NumberSpinnerBox
                        name="Minimum Circularity"
                        min={0}
                        max={1}
                        defaultValue={0.1}
                        step={0.05}
                    />
                    <NumberSpinnerBox
                        name="Minimum Area"
                        min={0}
                        defaultValue={5000}
                        step={10}
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