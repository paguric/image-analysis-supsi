import NumberSpinnerBox from './NumberSpinnerBox';
import ButtonGroupBox from './ControlPanelButtonGroup';

function ControlPanel({
    startingWavelength,
    finalWavelength,
    actualFrame = 0,
    onFrameChange,
    totalFrameCount
}) {

    return (
        <div className="grid grid-cols-1 gap-4 mt-4 ">
            <NumberSpinnerBox
                name={`Actual Frame (max allowed: ${totalFrameCount})`}
                min={0}
                defaultValue={isNaN(Number(actualFrame)) ? 0 : Number(actualFrame)}
                step={1}
                onChange={onFrameChange}
            />

            <NumberSpinnerBox
                name="High Pass Filter Window Size"
                min={0}
                defaultValue={101}
                step={2}
            />
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

            <ButtonGroupBox
                abortAndNavigateTo={`/differential-view/${startingWavelength}/${finalWavelength}/${totalFrameCount}/${actualFrame}`}
                saveAndNavigateTo={`/differential-view/${startingWavelength}/${finalWavelength}/${totalFrameCount}/${actualFrame}`}
            />
        </div>
    );
}

export default ControlPanel;