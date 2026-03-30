import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';

function valuetext(value) {
  return `${value} Frame`;
}

export default function DiscreteSlider({numberOfFrames, onChange}) {
  return (
    <Box sx={{ width: '100%' }}>
      <Slider
        aria-label="Frame"
        defaultValue={0}
        getAriaValueText={valuetext}
        valueLabelDisplay="auto"
        shiftStep={0}
        step={1}
        marks={true}
        min={0}
        max={numberOfFrames}
        onChange={(e, value) => onChange(value)}
      />
    </Box>
  );
}
