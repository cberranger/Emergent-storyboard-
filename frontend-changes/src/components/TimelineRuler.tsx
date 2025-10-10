interface TimelineRulerProps {
  duration: number;
  zoom: number;
}

export function TimelineRuler({ duration, zoom }: TimelineRulerProps) {
  const markers = [];
  const markerInterval = zoom < 10 ? 10 : zoom < 20 ? 5 : 1;

  for (let i = 0; i <= duration; i += markerInterval) {
    markers.push(i);
  }

  return (
    <div className="relative h-8 bg-neutral-900 border-b border-neutral-800 select-none">
      {markers.map((time) => (
        <div
          key={time}
          className="absolute top-0 h-full flex items-end"
          style={{ left: `${time * zoom}px` }}
        >
          <div className="flex flex-col items-center">
            <span className="text-xs text-neutral-400 mb-1">{time}s</span>
            <div className="w-px h-2 bg-neutral-600" />
          </div>
        </div>
      ))}
    </div>
  );
}
