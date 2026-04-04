import Button from '@mui/material/Button';
import VideoSlot from '../components/VideoSlot'
import { useHome } from '../hooks/HomeSetup'
import MaterialNumberField from '../components/ColorTextField';
import { useState } from 'react'
import InfoPopupWindow from '../components/InfoPopupWindow';


function Home() {


  const [startingWaveLenght, setStartingWaveLenght] = useState(0);

  const {
    loading,
    response,
    videoPrima, setVideoPrima,
    videoDopo, setVideoDopo,
    analyze
  } = useHome({ startingWaveLenght: startingWaveLenght });

  return (
    <div className="max-w-5xl mx-auto px-8 py-8 min-h-screen flex flex-col justify-center items-center">
      <h1 className="text-center text-2xl font-bold mb-8">Image Analysis</h1>

      <div className="flex justify-center gap-5 flex-wrap mb-8">
        <VideoSlot
          titolo="Video Before"
          fileSelezionato={videoPrima}
          setFileSelezionato={setVideoPrima}
        />
        <VideoSlot
          titolo="Video After"
          fileSelezionato={videoDopo}
          setFileSelezionato={setVideoDopo}
        />
      </div>

      {response && <p className="mb-4 text-sm">{response}</p>}

      <div className="flex">
        <MaterialNumberField
          label={"Starting Wavelength"}
          color={"info"}
          onChange={setStartingWaveLenght}
        />
      </div>

      <div className="p-8 flex flex-col items-center gap-4">
        <Button
          onClick={analyze}
          disabled={loading}
          variant="outlined" aria-label="Basic button group"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </Button>
      </div>

      <div>
        <InfoPopupWindow title={"home_title"} description={"home_description"} />
      </div>

    </div>
  )
}

export default Home