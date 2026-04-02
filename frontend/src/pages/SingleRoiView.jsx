import ControlPanel from '../components/ControlPanel'
import { ImgBox } from '../components/ImgBox';
import { useParams } from 'react-router-dom'
import { useSingleRoiView } from '../hooks/SingleRoiViewSetup';
import ImageGrid from '../components/ImageGrid';
import CircularIndeterminate from '../components/CircularIndeterminate';

function SingleRoiView() {

    const { roiNumber, frameNumber, startingWaveLenght } = useParams()

    const {
        stepUrls,
        isLoading,
        isBeforeLoading,
        isAfterLoading,
        isDiffLoading,
        beforeImgUrl,
        afterImgUrl,
        diffImgUrl
    } = useSingleRoiView(roiNumber, frameNumber);

    const items = stepUrls.map((url, i) => ({ img: url, title: `Step ${i}` }));

    return (
        <div className="flex h-screen w-full">

            {/* Colonna sinistra */}
            <div className="w-1/4 p-4 border-r">

                <p className="text-center font-bold text-2xl">ROI #{roiNumber}</p>
                <p>Current Wavelengh: {Number(startingWaveLenght) + Number(frameNumber)}</p>
                <ControlPanel startingWavelength={startingWaveLenght} actualFrame={frameNumber} />
            </div>


            {/* Colonna destra */}
            <div className="w-3/4 p-4 h-full">
                <div className="grid grid-cols-6 grid-rows-[1fr_2fr] h-full gap-2">

                    {
                        isBeforeLoading ? <CircularIndeterminate /> :
                            <ImgBox src={beforeImgUrl} stepName={"Before"} />
                    }



                    {
                        isAfterLoading ? <CircularIndeterminate /> :
                            <ImgBox src={afterImgUrl} stepName={"After"} />
                    }


                    {
                        isDiffLoading ? <CircularIndeterminate /> :
                            <ImgBox src={diffImgUrl} stepName={"Differential"} />
                    }


                    <div className="col-span-3" >
                        {
                            isLoading ? <CircularIndeterminate /> :
                                <ImageGrid items={items} />
                        }
                    </div>

                    <div className="col-span-3">
                        {
                            <ImgBox src="../../img/placeholder.png" />
                        }
                    </div>

                </div>
            </div>
        </div>
    )
}
export default SingleRoiView