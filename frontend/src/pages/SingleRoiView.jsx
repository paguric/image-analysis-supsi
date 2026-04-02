// SingleRoiView.jsx
import ControlPanel from '../components/ControlPanel';
import { ImgBox } from '../components/ImgBox';
import { useParams, useNavigate } from 'react-router-dom';
import { useSingleRoiView } from '../hooks/SingleRoiViewSetup';
import ImageGrid from '../components/ImageGrid';
import CircularIndeterminate from '../components/CircularIndeterminate';
import { useRef } from 'react';

function SingleRoiView() {

    const { roiNumber, frameNumber, startingWaveLenght } = useParams();
    const navigate = useNavigate();

    const debounceTimer = useRef(null);

    const {
        stepUrls,
        isLoading,
        isBeforeLoading,
        isAfterLoading,
        isDiffLoading,
        beforeImgUrl,
        afterImgUrl,
        diffImgUrl,
    } = useSingleRoiView(roiNumber, frameNumber);

    const handleFrameChange = (newFrame) => {
        if (debounceTimer.current) {
            clearTimeout(debounceTimer.current);
        }

        debounceTimer.current = setTimeout(() => {
            navigate(`/single-roi-view/${roiNumber}/${newFrame}/${startingWaveLenght}`, { replace: true });
        }, 180); 
    };

    const items = stepUrls.map((url, i) => ({ img: url, title: `Step ${i}` }));

    const currentWavelength = Number(startingWaveLenght) + Number(frameNumber);

    return (
        <div className="flex h-screen w-full overflow-hidden">

            {/* Colonna sinistra  */}
            <div className="w-1/4 p-6 border-r bg-gray-50 overflow-y-auto">
                <div className="mb-6">
                    <p className="text-center font-bold text-3xl mb-1">ROI #{roiNumber}</p>
                    <p className="text-center text-gray-600">
                        Current Wavelength: <strong>{currentWavelength}</strong>
                    </p>
                </div>

                <ControlPanel 
                    startingWavelength={startingWaveLenght} 
                    actualFrame={frameNumber} 
                    onFrameChange={handleFrameChange}
                />
            </div>

            {/* Colonna destra */}
            <div className="w-3/4 p-4 h-full overflow-hidden">
                <div className="grid grid-cols-6 grid-rows-[1fr_2fr] h-full gap-3">

                    <div className="col-span-2">
                        {isBeforeLoading ? (
                            <CircularIndeterminate />
                        ) : (
                            <ImgBox src={beforeImgUrl} stepName="Before" />
                        )}
                    </div>

                    <div className="col-span-2">
                        {isAfterLoading ? (
                            <CircularIndeterminate />
                        ) : (
                            <ImgBox src={afterImgUrl} stepName="After" />
                        )}
                    </div>

                    <div className="col-span-2">
                        {isDiffLoading ? (
                            <CircularIndeterminate />
                        ) : (
                            <ImgBox src={diffImgUrl} stepName="Differential" />
                        )}
                    </div>

  
                    <div className="col-span-3 row-span-1">
                        {isLoading ? (
                            <CircularIndeterminate />
                        ) : (
                            <ImageGrid items={items} />
                        )}
                    </div>

                    <div className="col-span-3 row-span-1">
                        <ImgBox src="../../img/placeholder.png" stepName="Other View" />
                    </div>

                </div>
            </div>
        </div>
    );
}

export default SingleRoiView;