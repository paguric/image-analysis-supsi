import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';

function DifferentialViewButtonGroup({ showContours, isContoursLoading, onToggleContours }) {
    return (
        <ButtonGroup fullWidth>
            <Button
                onClick={onToggleContours}
                disabled={isContoursLoading}
                variant={showContours ? 'contained' : 'outlined'}
            >
                {isContoursLoading ? 'Loading...' : 'Show Contours'}
            </Button>
            <Button>Export CSV</Button>
        </ButtonGroup>
    )
}

export default DifferentialViewButtonGroup
