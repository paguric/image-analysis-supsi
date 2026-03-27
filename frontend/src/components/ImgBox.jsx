export const ImgBox = ({ src, className = "col-span-2", fill = false }) => (
  <div className={`${className} flex items-center justify-center overflow-hidden w-full h-full`}>
    <img className={`w-full h-full ${fill ? 'object-cover' : 'object-contain'}`} src={src} />
  </div>
)