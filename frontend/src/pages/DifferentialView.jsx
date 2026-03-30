import { useNavigate } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react';
import Button from '@mui/material/Button';
import { ImgBox } from '../components/ImgBox';
import DifferentialViewButtonGroup from '../components/DifferentialViewButtonGroup'
import DiscreteSlider from '../components/DiscreteSlider';
import { getDifferentialFrame, getNumberOfFrames } from "../services/pipelineApi";
import { getRoiCount } from '../services/roiApi';
import CircularIndeterminate from '../components/CircularIndeterminate';


function DifferentialView() {

    const navigate = useNavigate()

    const [numberOfRois, setNumberOfRois] = useState(0);
    const [frameCount, setFrameCount] = useState(100);
    const [urlDiff, setUrlDiff] = useState(null);
    const [currentFrame, setCurrentFrame] = useState(0);
    const prevDiffUrl = useRef(null);
    const debounceTimer = useRef(null);
    const [isLoading, setIsLoading] = useState(true);

    async function loadDiffFrame(frame) {
        setIsLoading(true);
        try {
            const url = await getDifferentialFrame(frame);
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current);
            prevDiffUrl.current = url;
            setUrlDiff(url);
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        loadDiffFrame(currentFrame);
    }, [currentFrame]);

    useEffect(() => {
        getNumberOfFrames()
            .then(data => setFrameCount(data.total_frames))
            .catch(err => console.error(err));
    }, []);

    useEffect(() => {
        getRoiCount()
            .then(data => setNumberOfRois(data))
            .catch(err => console.error(err));
    }, []);

    useEffect(() => {
        return () => {
            if (prevDiffUrl.current)
                URL.revokeObjectURL(prevDiffUrl.current);
        }
    }, []);

    return (
        <div className="flex h-screen w-full">

            {/* Colonna sinistra */}
            <div className="w-1/5 p-4 border-r">
                <div className="flex flex-col gap-2">
                    {Array.from({ length: numberOfRois }, (_, i) => (
                        <div key={i} className="flex border p-2 rounded items-center justify-center">
                            <Button onClick={() => navigate(`/single-roi-view/${i + 1}`)}>
                                ROI {i + 1}
                            </Button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Colonna destra */}
            <div className="w-4/5 p-4 h-full">
                <div className="grid grid-cols-1 grid-rows-7 h-full gap-2">
                    <div className="row-span-4 flex items-center justify-center">
                        {isLoading
                            ? <CircularIndeterminate />
                            : urlDiff && <ImgBox src={urlDiff} />
                        }
                    </div>

                    <div className="row-span-1 flex w-full justify-center">
                        <DifferentialViewButtonGroup className="w-full" />
                    </div>

                    <div className="w-full">
                        <Button className="w-full" variant="outlined"
                            onClick={() => navigate('/')}>
                            Take another Analysis
                        </Button>
                    </div>

                    <div>
                        <DiscreteSlider numberOfFrames={frameCount} onChange={(value) => {
                            if (debounceTimer.current)
                                clearTimeout(debounceTimer.current);
                            debounceTimer.current = setTimeout(() => {
                                setCurrentFrame(value);
                            }, 150);
                        }} />
                        <p>Frame corrente: {currentFrame}</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default DifferentialView