import Button from '@mui/material/Button';
import { ImgBox } from '../components/ImgBox';
import DifferentialViewButtonGroup from '../components/DifferentialViewButtonGroup'
import DiscreteSlider from '../components/DiscreteSlider';
import CircularIndeterminate from '../components/CircularIndeterminate';

import { useDifferentialView } from '../hooks/DifferentialViewSetup'
import { useParams } from 'react-router-dom';
import { computeWaveLength } from '../hooks/ComputeActualWaveLen';
import { clearDataBase } from '../services/analysisApi'
import { useSetInfoPopup } from '../hooks/useSetInfoPopup'
import { useFileSelector } from '../hooks/FileSelector'

function DifferentialView() {
    useSetInfoPopup("differential_view_title", "differential_description")

    const { startingWaveLenght, finalWaveLenght, totalFrameCount, actualFrame } = useParams();

    
    const {
        navigate,
        numberOfRois,
        currentFrame,
        setCurrentFrame,
        urlDiff,
        urlDiffContours,
        showContours,
        toggleContours,
        isContoursLoading,
        debounceTimer,
        isLoading
    } = useDifferentialView(actualFrame);



    const currentWavelength = computeWaveLength(    startingWaveLenght, finalWaveLenght, 
                                                    currentFrame, totalFrameCount
                                                );


    return (
        <div className="flex h-screen w-full overflow-hidden">

            {/* colonna sinistra */}
            <div className="w-1/5 border-r border-gray-200 dark:border-gray-700 flex flex-col">

                <div className="p-4 border-b dark:border-gray-700 font-medium text-gray-700 dark:text-gray-200">
                    <div className="flex justify-center">
                        ROIs List
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-2">

                    {Array.from({ length: numberOfRois }, (_, i) => (
                        <div key={i} className="flex">
                            <Button
                                fullWidth
                                variant="outlined"
                                onClick={() => navigate(
                                    `/single-roi-view/${i}/${currentFrame}/${totalFrameCount}/${startingWaveLenght}/${finalWaveLenght}`
                                )}
                            >
                                ROI {i + 1}
                            </Button>
                        </div>
                    ))}
                </div>
            </div>



            {/*colonna destra */}
            <div className="w-4/5 flex flex-col h-full p-4 gap-3 overflow-hidden">

                {/* Immagine - occupa la maggior parte dello spazio */}
                <div className="flex-1 min-h-0 flex items-center justify-center bg-black rounded-lg overflow-hidden">
                    {isLoading ? (
                        <CircularIndeterminate />
                    ) : <ImgBox src={showContours ? urlDiffContours : urlDiff} />}
                </div>

                {/* Parte inferiore - dimensione naturale, non si schiaccia */}
                <div className="shrink-0 flex flex-col gap-3">

                    <div className="flex items-center justify-center">
                        <DifferentialViewButtonGroup
                            className="w-full max-w-2xl"
                            showContours={showContours}
                            isContoursLoading={isContoursLoading}
                            onToggleContours={toggleContours}

                            // onCsvExport={handleCsvExport}
                        />
                    </div>

                    <div>
                        <Button
                            className="w-full"
                            variant="outlined"
                            onClick={() => (
                                        clearDataBase(),
                                        navigate('/'))}
                        >
                            Take another Analysis
                        </Button>
                    </div>

                    <div className="space-y-2">
                        <DiscreteSlider
                            startingValue={actualFrame}
                            numberOfFrames={totalFrameCount}
                            onChange={(value) => {
                                if (debounceTimer.current)
                                    clearTimeout(debounceTimer.current);
                                debounceTimer.current = setTimeout(() => {
                                    setCurrentFrame(value);
                                }, 150);
                            }}
                        />
                        <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                            <p>Current Frame: <strong>{currentFrame}</strong></p>
                            <p>Current Wavelength: <strong>{Number(currentWavelength).toFixed(2)} nm</strong></p>
                        </div>

                    </div>

                </div>
            </div>
        </div>
    )
}

export default DifferentialView