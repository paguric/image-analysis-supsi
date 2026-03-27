import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import DifferentialView from './components/DifferentialView'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/differential-view" element={<DifferentialView />} />
    </Routes>
  )
}

export default App