import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import SingleRoiView from './pages/SingleRoiView'
import DifferentialView from './pages/DifferentialView'
import DarkModeToggle from './components/DarkModeToggle'
import InfoPopupWindow from './components/InfoPopupWindow'
import { useInfoPopup } from './context/ThemeContext'

function App() {
  const { infoProps } = useInfoPopup()

  return (
    <>
      <div style={{ position: 'fixed', top: 7, left: 12, zIndex: 9999, display: 'flex', alignItems: 'center', gap: 4 }}>
        <DarkModeToggle />
        {infoProps && <InfoPopupWindow title={infoProps.title} description={infoProps.description} />}
      </div>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/differential-view/:startingWaveLenght/:finalWaveLenght/:totalFrameCount/:actualFrame" element={<DifferentialView/>}/>
        <Route path="/single-roi-view/:roiNumber/:frameNumber/:totalFrameCount/:startingWaveLenght/:finalWaveLenght/" element={<SingleRoiView />} />
      </Routes>
    </>
  )
}

export default App