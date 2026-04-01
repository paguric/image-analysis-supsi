import ControlPanel from '../components/ControlPanel'
import { ImgBox } from '../components/ImgBox';
import { useParams } from 'react-router-dom'
import { useSingleRoiView } from '../hooks/SingleRoiViewSetup';



function SingleRoiView() {

    const {roiNumber} = useParams()

    const {
        stepUrls,
        isLoading,
        error
    } = useSingleRoiView();

    

    return (
        <div className="flex h-screen w-full">

            {/* Colonna sinistra */}
            <div className="w-1/4 p-4 border-r">

                <p className="text-center font-bold text-2xl">ROI #{roiNumber}</p>

                <ControlPanel/>
            </div>


            {/* Colonna destra */}
            <div className="w-3/4 p-4 h-full">
                <div className="grid grid-cols-6 grid-rows-3 h-full gap-2">
                    <ImgBox src="../../img/placeholder.png" fill/>
                    <ImgBox src="../../img/placeholder.png" fill/>
                    <ImgBox src="../../img/placeholder.png" fill/>

                    <ImgBox src="../../img/placeholder.png" className="col-span-3 row-span-3" fill/>
                    <ImgBox src="../../img/placeholder.png" className="col-span-3 row-span-3" fill/>
                </div>
            </div>
        </div>
    )
}
    export default SingleRoiView