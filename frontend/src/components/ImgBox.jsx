export const ImgBox = ({ src, className = "col-span-2", fill = false, stepName }) => (
  <div className={`${className} flex flex-col items-center justify-center overflow-hidden w-full h-full`}>
    {stepName && <p className="text-sm font-semibold text-center w-full mb-1">{stepName}</p>}
    <img className={`w-full h-full ${fill ? 'object-cover' : 'object-contain'}`} src={src} />
  </div>
)