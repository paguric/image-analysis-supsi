function VideoPlayer({ src }) {
  return (
    <div className="mt-2 w-full">
      <video key={src} controls width="100%" src={src}>
        Your browser does not support video playback.
      </video>
    </div>
  )
}

export default VideoPlayer