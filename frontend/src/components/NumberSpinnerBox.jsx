import Box from '@mui/material/Box';
import NumberSpinner from './NumberSpinner';

function NumberSpinnerBox({
  name,
  min,
  max,
  defaultValue,
  step = 1,
  onChange,
  error = false,
  odd = false
}) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
      }}
    >
      <NumberSpinner
        label={name}
        min={min}
        max={max}
        defaultValue={defaultValue}
        step={step}
        size="small"
        onValueChange={onChange}
        error={error}
        odd={odd}
      />
    </Box>
  );
}

export default NumberSpinnerBox;