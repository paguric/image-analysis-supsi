import { useState } from 'react'
import api from './api'
import './App.css'

function App() {
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)

  const callBackend = async () => {
    setLoading(true)
    try {
      const res = await api.get('/')
      setResponse(res.data.message)
    } catch (err) {
      setResponse('Error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h1>Frontend ↔ Backend</h1>
      <div className="card">
        <button onClick={callBackend} disabled={loading}>
          {loading ? 'Loading...' : 'Call Backend'}
        </button>
        {response && <p>Response: <strong>{response}</strong></p>}
      </div>
    </>
  )
}

export default App
