import { useNavigate } from 'react-router-dom'
import ControlPanel from './ControlPanel'

// DifferentialView.jsx
function DifferentialView() {
  return (
    <div className="flex h-screen">
      
      {/* Colonna sinistra */}
      <div className="w-1/3 p-4 border-r">
        <ControlPanel />
      </div>

      {/* Colonna destra
      <div className="w-2/3 p-4">
        <VideoGrid />
        <VideoDetail />
      </div> */}

    </div>
  )
}

 export default DifferentialView