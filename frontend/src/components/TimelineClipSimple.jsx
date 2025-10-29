import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

const TimelineClipSimple = ({
  clip,
  zoom,
  trackY,
  clipIndex,
  onClick,
  backgroundColor = 'bg-slate-400',
  hoverColor = 'hover:bg-slate-500'
}) => {
  const clipStart = (clip.timeline_position || 0) * zoom;
  const clipWidth = (clip.length || 5) * zoom;

  return (
    <div
      className={`absolute h-4 ${backgroundColor} ${hoverColor} rounded border border-slate-300 flex items-center px-1 cursor-pointer transition-colors`}
      style={{
        left: `${clipStart}px`,
        width: `${clipWidth}px`,
        top: `${trackY}px`
      }}
      onClick={() => onClick?.(clip)}
    >
      <span className="text-xs font-medium text-slate-800 truncate">
        {clip.name}
      </span>
    </div>
  );
};

export default TimelineClipSimple;
