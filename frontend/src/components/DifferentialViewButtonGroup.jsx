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

            <Button
                // onClick={onCsvExport}
            >
                Export CSV (Global)
            </Button>

            <Button>
                Export Frame CSV (Pixel by Pixel)
            </Button>

        </ButtonGroup>
    )
}

export default DifferentialViewButtonGroup
