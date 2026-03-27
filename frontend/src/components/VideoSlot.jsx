import VideoUploader from './VideoUploader'
import VideoPlayer from './VideoPlayer'

function VideoSlot({ titolo, fileSelezionato, setFileSelezionato, videoUrl, solaLettura }) {
  return (
    <div className="bg-[#1a1a1a] p-4 rounded-xl w-80 shadow-lg flex flex-col gap-4">
      <h3 className="m-0 text-xl text-white">{titolo}</h3>
      
      {videoUrl ? (
        <VideoPlayer src={videoUrl} />
      ) : solaLettura ? (
        <div className="border-2 border-dashed border-[#444] rounded-lg p-5 text-center text-[#888] bg-white/[0.02] flex items-center justify-center flex-grow">
          <p>In attesa del video elaborato...</p>
        </div>
      ) : fileSelezionato ? (
        <div className="border-2 border-dashed border-[#666] rounded-lg p-5 text-center text-[#aaa] bg-white/5">
          <p>File pronto: <strong>{fileSelezionato.name}</strong></p>
        </div>
      ) : (
        <VideoUploader onVideoSelected={setFileSelezionato} />
      )}
    </div>
  )
}

export default VideoSlot