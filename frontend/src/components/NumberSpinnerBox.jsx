import Box from '@mui/material/Box';
import NumberSpinner from './NumberSpinner';

function NumberSpinnerBox({ 
  name, 
  min, 
  defaultValue, 
  step = 1, 
  onChange 
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
        defaultValue={defaultValue} 
        step={step} 
        size="small"
        onValueChange={onChange}    
      />
    </Box>
  );
}

export default NumberSpinnerBox;