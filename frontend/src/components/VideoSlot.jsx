import VideoUploader from './VideoUploader'
import VideoPlayer from './VideoPlayer'

function VideoSlot({ deletable, titolo, fileSelezionato, setFileSelezionato, videoUrl, solaLettura }) {
  return (
    <div className="bg-[#1a1a1a] p-4 rounded-xl w-80 shadow-lg flex flex-col gap-4">
      <div className="flex justify-center">
        <h3 className="m-0 text-xl text-white">{titolo}</h3>
      </div>
      
      
      {videoUrl ? (
        <VideoPlayer src={videoUrl} />
      ) : solaLettura ? (
        <div className="border-2 border-dashed border-[#444] rounded-lg p-5 text-center text-[#888] bg-white/[0.02] flex items-center justify-center flex-grow" />
      ) : fileSelezionato ? (
        <div className="relative border-2 border-dashed border-[#666] rounded-lg p-5 text-center text-[#aaa] bg-white/5">
          {deletable && (
            <span
              onClick={() => setFileSelezionato(null)}
              className="absolute top-1 right-1 w-7 h-7 flex items-center justify-center rounded-full text-white/40 hover:text-white hover:bg-black text-2xl cursor-pointer transition-all"
            >
              &times;
            </span>
          )}
          <p>File: <strong>{typeof fileSelezionato === 'string' ? fileSelezionato.split(/[/\\]/).pop() : fileSelezionato.name}</strong></p>
        </div>
      ) : (
        <VideoUploader onVideoSelected={setFileSelezionato} />
      )}
    </div>
  )
}

export default VideoSlot