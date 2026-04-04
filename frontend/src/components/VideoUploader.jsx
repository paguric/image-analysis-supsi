import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

function VideoUploader({ onVideoSelected }) {
  
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      onVideoSelected(file)
    }
  }, [onVideoSelected])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 
      'video/x-msvideo': ['.avi'],
      'video/*': ['.mp4', '.mkv']
    },
    multiple: false
  })

  return (
    <div 
      {...getRootProps()} 
      className={`border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-all duration-200 bg-white/5
        ${isDragActive 
          ? 'border-green-500 bg-green-500/10 text-white' 
          : 'border-[#666] text-[#aaa] hover:border-[#888] hover:bg-white/10'
        }`}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p className="m-0 text-sm">Drop the video here...</p>
      ) : (
        <p className="m-0 text-sm">Drag the video you want to analyze (.avi) here, or click</p>
      )}
    </div>
  )
}

export default VideoUploader