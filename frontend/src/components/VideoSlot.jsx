import VideoUploader from './VideoUploader'
import VideoPlayer from './VideoPlayer'
import styles from '../css/VideoSlot.module.css'

/**
 * @class VideoSlot 
 * @brief rappresenta lo slot completo che combina uploader e player
 */
function VideoSlot({ titolo, fileSelezionato, setFileSelezionato, videoUrl, solaLettura }) {
  return (
    <div className={styles.finestraVideo}>
      <h3 className={styles.titoloVideo}>{titolo}</h3>
      
      {/* @brief rendering condizionale per slot di input o di output */}
      {/* @details se c'è un url mostriamo il player. Se lo slot è di output (solaLettura), mostriamo un riquadro vuoto in attesa, altrimenti proseguiamo con le logiche di upload */}
      {videoUrl ? (
        <VideoPlayer src={videoUrl} />
      ) : solaLettura ? (
        <div className={styles.areaAttesa}>
          <p>In attesa del video elaborato...</p>
        </div>
      ) : fileSelezionato ? (
         <div className={styles.areaDrop}>
           <p>File pronto: <strong>{fileSelezionato.name}</strong></p>
         </div>
      ) : (
        <VideoUploader onVideoSelected={setFileSelezionato} />
      )}
    </div>
  )
}

export default VideoSlot