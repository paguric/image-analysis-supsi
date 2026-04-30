import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';


function DifferentialViewButtonGroup({ showContours,
                                       isContoursLoading,
                                       onToggleContours,
                                       onFrameCsvExport,
                                       isExportingFrame,
                                       onGlobalCsvExport,
                                       isExportingGlobal,
                                    }) {
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
                onClick={onGlobalCsvExport}
                disabled={isExportingGlobal}
            >
                {isExportingGlobal ? 'Exporting...' : 'Export CSV (Global)'}
            </Button>

            <Button
                onClick={onFrameCsvExport}
                disabled={isExportingFrame}
            >
                {isExportingFrame ? 'Exporting...' : 'Export Frame CSV (Pixel by Pixel)'}
            </Button>

        </ButtonGroup>
    )
}

export default DifferentialViewButtonGroup
