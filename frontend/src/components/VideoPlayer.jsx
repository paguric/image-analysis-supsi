// @brief importazione corretta del modulo css
import styles from '../css/VideoSlot.module.css'

/**
 * @class VideoPlayer 
 * @brief componente grafico puro per riprodurre un video
 */
function VideoPlayer({ src }) {
  return (
    <div className={styles.playerWrapper}>
      {/* @brief elemento video nativo */}
      <video controls width="100%" src={src}>
        Il browser non supporta la riproduzione video.
      </video>
    </div>
  )
}

export default VideoPlayer