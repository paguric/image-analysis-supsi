import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import SingleRoiView from './pages/SingleRoiView'
import DifferentialView from './pages/DifferentialView'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/differential-view/:startingWaveLenght/:actualFrame" element={<DifferentialView/>}/>
      <Route path="/single-roi-view/:roiNumber/:frameNumber/:startingWaveLenght" element={<SingleRoiView />} />
    </Routes>
  )
}

export default App