import Button from '@mui/material/Button';
import { ImgBox } from '../components/ImgBox';
import DifferentialViewButtonGroup from '../components/DifferentialViewButtonGroup'
import DiscreteSlider from '../components/DiscreteSlider';
import CircularIndeterminate from '../components/CircularIndeterminate';

import { useDifferentialView } from '../hooks/DifferentialViewSetup'
import { useParams } from 'react-router-dom';

function DifferentialView() {

    const { startingWaveLenght, actualFrame } = useParams();

    const {
        navigate,
        numberOfRois,
        frameCount,
        currentFrame,
        setCurrentFrame,
        urlDiff,
        debounceTimer,
        isLoading,
    } = useDifferentialView();

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
                                onClick={() => navigate(`/single-roi-view/${i + 1}/${currentFrame}/${startingWaveLenght}`)}
                            >
                                ROI {i + 1}
                            </Button>
                        </div>
                    ))}
                </div>
            </div>



            {/*colonna destra */}
            <div className="w-4/5 flex flex-col h-full">

                <div className="flex-1 p-4 overflow-hidden">
                    <div className="grid grid-cols-1 grid-rows-7 h-full gap-3">

                        <div className="row-span-4 flex items-center justify-center bg-black rounded-lg overflow-hidden">
                            {isLoading ? (
                                <CircularIndeterminate />
                            ) : urlDiff && <ImgBox src={urlDiff} />}
                        </div>

                        <div className="row-span-1 flex items-center justify-center">
                            <DifferentialViewButtonGroup className="w-full max-w-2xl" />
                        </div>

                        <div>
                            <Button
                                className="w-full"
                                variant="outlined"
                                onClick={() => navigate('/')}
                            >
                                Take another Analysis
                            </Button>
                        </div>

                        <div className="space-y-2">
                            <DiscreteSlider
                                startingValue={actualFrame}
                                numberOfFrames={frameCount}
                                onChange={(value) => {
                                    if (debounceTimer.current) clearTimeout(debounceTimer.current);
                                    debounceTimer.current = setTimeout(() => {
                                        setCurrentFrame(value);
                                    }, 150);
                                }}
                            />
                            <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                                <p>Current Frame: <strong>{currentFrame}</strong></p>
                                <p>Current Wavelength: <strong>{Number(currentFrame) + Number(startingWaveLenght)}</strong></p>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    )
}

export default DifferentialView