import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import SingleRoiView from './pages/SingleRoiView'
import DifferentialView from './pages/DifferentialView'
import DarkModeToggle from './components/DarkModeToggle'

function App() {
  return (
    <>
      <DarkModeToggle />
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/differential-view/:startingWaveLenght/:finalWaveLenght/:actualFrame" element={<DifferentialView/>}/>
        <Route path="/single-roi-view/:roiNumber/:frameNumber/:startingWaveLenght/:finalWaveLenght/" element={<SingleRoiView />} />
      </Routes>
    </>
  )
}

export default App