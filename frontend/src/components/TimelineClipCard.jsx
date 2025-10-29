import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ImageIcon, Wand2, Copy } from 'lucide-react';

const TimelineClipCard = ({
  clip,
  isSelected,
  zoom,
  trackY,
  clipIndex,
  onSelect,
  onGenerate,
  onCreateAlternate,
  getClipColor
}) => {
  const clipStart = (clip.timeline_position || 0) * zoom;
  const clipWidth = (clip.length || 5) * zoom;

  const handleClick = () => {
    onSelect?.(clip);
  };

  const handleGenerate = (e) => {
    e.stopPropagation();
    onGenerate?.(clip);
  };

  const handleCreateAlternate = (e) => {
    e.stopPropagation();
    onCreateAlternate?.(clip.id);
  };

  return (
    <div
      className={`absolute h-12 rounded ${getClipColor?.(clip) || 'bg-slate-500'} border ${
        isSelected ? 'border-indigo-500 ring-2 ring-indigo-500' : 'border-gray-600'
      } hover:border-gray-500 flex flex-col justify-between p-2 cursor-pointer transition-all`}
      style={{
        left: `${clipStart}px`,
        width: `${clipWidth}px`,
        top: `${trackY + clipIndex * 2}px`,
        minWidth: '60px'
      }}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between min-w-0">
        <span className="text-[11px] font-medium text-gray-200 truncate flex-1">
          {clip.name}
        </span>
        {clip.is_alternate && (
          <Badge variant="secondary" className="text-[8px] h-3 px-1 ml-1">
            A{clip.alternate_number}
          </Badge>
        )}
      </div>

      <div className="flex items-center justify-between">
        <span className="text-[10px] text-gray-400">
          {clip.length}s
        </span>
        <div className="flex items-center space-x-1">
          {clip.generated_images?.length > 0 && (
            <ImageIcon className="w-3 h-3 text-green-400" />
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleGenerate}
            className="h-4 w-4 p-0 hover:bg-gray-600"
          >
            <Wand2 className="w-3 h-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCreateAlternate}
            className="h-4 w-4 p-0 hover:bg-gray-600"
          >
            <Copy className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TimelineClipCard;
