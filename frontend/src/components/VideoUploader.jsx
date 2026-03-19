import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import styles from '../css/VideoSlot.module.css'

/**
 * @class VideoUploader 
 * @brief gestisce l'area di drag & drop per caricare il video da analizzare
 */
function VideoUploader({ onVideoSelected }) {
  
  /**
   * @brief gestisce i file rilasciati
   * @details invece di creare un URL locale, passiamo direttamente l'oggetto File al genitore per l'invio al backend
   */
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      // @brief propaga l'oggetto File nativo verso il genitore
      onVideoSelected(file)
    }
  }, [onVideoSelected])

  // @brief configurazione della dropzone
  // @details abilitiamo specificamente le estensioni .avi e i formati video generici
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
      className={`${styles.areaDrop} ${isDragActive ? styles.areaDropAttiva : ''}`}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Rilascia il video qui...</p>
      ) : (
        <p>Trascina il video da analizzare (.avi), o clicca</p>
      )}
    </div>
  )
}

export default VideoUploader