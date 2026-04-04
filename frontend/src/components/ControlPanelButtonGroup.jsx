import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import Box from '@mui/material/Box';
import { useNavigate } from 'react-router-dom'


export default function ControlPanelButtonGroup({abortAndNavigateTo, saveAndNavigateTo}) {

  const navigate = useNavigate()

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        '& > *': {
          m: 1,
        },
      }}
    >
      <ButtonGroup variant="outlined" aria-label="Basic button group">
        <Button color="error" onClick={() => navigate(abortAndNavigateTo)}>Abort</Button>
        
        <Button variant="outlined" 
                color="success" 
                onClick={() => navigate(saveAndNavigateTo)}
        >Save</Button>

      </ButtonGroup>
    </Box>
  );
}
