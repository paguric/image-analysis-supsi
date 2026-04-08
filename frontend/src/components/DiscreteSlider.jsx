import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';

function valuetext(value) {
  return `${value} Frame`;
}

function computeSum(first, second) {
  return first + second;
}

export default function DiscreteSlider({startingValue, numberOfFrames, onChange}) {
  return (
    <Box sx={{ width: '100%' }}>
      
      <Slider
        aria-label="Frame"
        defaultValue={startingValue}
        getAriaValueText={valuetext}
        valueLabelDisplay="auto"
        shiftStep={0}
        step={1}
        marks={true}
        min={1}
        max={numberOfFrames}
        onChange={(e, value) => onChange(value)}
      />
    </Box>
  );
}
