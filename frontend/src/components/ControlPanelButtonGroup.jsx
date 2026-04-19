import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import Box from '@mui/material/Box';
import { useNavigate } from 'react-router-dom'
import { saveRoiParametrization } from '../services/roiApi'


export default function ControlPanelButtonGroup({abortAndNavigateTo, saveAndNavigateTo}) {

  const navigate = useNavigate()

  const handleSave = async () => {
    try {
      await saveRoiParametrization();
    } catch (err) {
      console.error("Errore durante il salvataggio:", err);
      return;
    }
    navigate(saveAndNavigateTo);
  };

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
                onClick={handleSave}
        >Save</Button>

      </ButtonGroup>
    </Box>
  );
}
