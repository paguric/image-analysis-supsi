import Box from '@mui/material/Box';
import NumberSpinner from './NumberSpinner';

function NumberSpinnerBox({name, min, max, defaultValue}) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
        justifyContent: 'center',
      }}
    >
      <NumberSpinner label={name} min={min} max={max} defaultValue={defaultValue} size='small'/>
      
    </Box>
  );
}

    export default NumberSpinnerBox