import { useState, useRef, useCallback } from 'react';

export const ImgBox = ({ src, className = "col-span-2", fill = false, stepName, zoomable = false  }) => {
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const isDragging = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });

  const handleWheel = useCallback((e) => {
    e.preventDefault();
    setScale(prev => Math.min(Math.max(prev - e.deltaY * 0.001, 1), 8));
  }, []);

  const handleMouseDown = (e) => {
    isDragging.current = true;
    lastPos.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e) => {
    if (!isDragging.current) return;
    const dx = e.clientX - lastPos.current.x;
    const dy = e.clientY - lastPos.current.y;
    lastPos.current = { x: e.clientX, y: e.clientY };
    setOffset(prev => ({ x: prev.x + dx, y: prev.y + dy }));
  };

  const handleMouseUp = () => { isDragging.current = false; };

  const handleDoubleClick = () => {
    setScale(1);
    setOffset({ x: 0, y: 0 });
  };

  return (
    <div className={`${className} flex flex-col items-center justify-center overflow-hidden w-full h-full`}>
      {stepName && (
        <p className="text-sm font-semibold text-center w-full mb-1 shrink-0">{stepName}</p>
      )}
      <div
        className={`w-full min-h-0 flex-1 overflow-hidden ${zoomable ? 'cursor-grab active:cursor-grabbing' : ''}`}
        onWheel={zoomable ? handleWheel : undefined}
        onMouseDown={zoomable ? handleMouseDown : undefined}
        onMouseMove={zoomable ? handleMouseMove : undefined}
        onMouseUp={zoomable ? handleMouseUp : undefined}
        onMouseLeave={zoomable ? handleMouseUp : undefined}
        onDoubleClick={zoomable ? handleDoubleClick : undefined}
      >
        <img
          className={`w-full h-full ${fill ? 'object-cover' : 'object-contain'}`}
          src={src}
          draggable={false}
          style={{
            transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`,
            transformOrigin: 'center',
            transition: isDragging.current ? 'none' : 'transform 0.1s ease',
          }}
        />
      </div>
    </div>
  );
};