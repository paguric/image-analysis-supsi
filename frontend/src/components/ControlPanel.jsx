import NumberSpinnerBox from './NumberSpinnerBox';

export default function ControlPanel() {

    return (
        <>
            <NumberSpinnerBox name={"Blur Window Size"} min={0} defaultValue={101}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Morph Transformation Window Size"} min={0} defaultValue={3}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Morph Transformation Number of Iterations"} min={0} defaultValue={2}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Canny Low Treeshold"} min={0}  defaultValue={0}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Canny High Treeshold"} min={0}  defaultValue={0}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Mini"} min={0}  defaultValue={0}></NumberSpinnerBox>
            <NumberSpinnerBox name={"Canny Low Treeshold"} min={0}  defaultValue={0}></NumberSpinnerBox>
        </>

    )


}

