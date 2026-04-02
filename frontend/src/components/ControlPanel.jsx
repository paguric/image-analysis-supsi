import NumberSpinnerBox from './NumberSpinnerBox';
import ButtonGroupBox from './ControlPanelButtonGroup';

function ControlPanel({ minWaveLength = 0, maxWaveLength = 0, actualFrame = 0 }) {

    return (
        <> 
        <div className="grid grid-cols-1 gap-7">
            <NumberSpinnerBox name={"Actual Frame"} min={minWaveLength} max={maxWaveLength} defaultValue={actualFrame}></NumberSpinnerBox>
            <NumberSpinnerBox name={"High Pass Filter Window Size"} min={0} defaultValue={101}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Morph Transformation Window Size"} min={0} defaultValue={3}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Morph Transformation Number of Iterations"} min={0} defaultValue={2}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Canny Low Treeshold"} min={0}  defaultValue={0}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Canny High Treeshold"} min={0}  defaultValue={0}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Minimum Circularity"} min={0} max={1}  defaultValue={0.1}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Minimum Area"} min={0} defaultValue={5000}></NumberSpinnerBox>

            <ButtonGroupBox
            abortAndNavigateTo={"/differential-view"}
            saveAndNavigateTo={"/differential-view"}
            ></ButtonGroupBox>
        </div>
        </>
    )
}
    export default ControlPanel