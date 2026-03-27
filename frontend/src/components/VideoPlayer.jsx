function VideoPlayer({ src }) {
  return (
    <div className="mt-2 w-full">
      <video key={src} controls width="100%" src={src}>
        Il browser non supporta la riproduzione video.
      </video>
    </div>
  )
}

export default VideoPlayer