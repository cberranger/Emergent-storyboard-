import { useRef } from 'react';
import { useDrag } from 'react-dnd';
import { Badge } from './ui/badge';
import { GripHorizontal, Image, Video } from 'lucide-react';

const ItemTypes = {
  CLIP: 'clip'
};

interface DraggableClipProps {
  clip: any;
  version: any;
  versionIndex: number;
  sceneId: string;
  sceneStartTime: number;
  zoom: number;
  trackIndex: number;
  onClick: (clip: any) => void;
}

// Color schemes for different versions
const VERSION_COLORS = [
  { from: 'from-blue-600', to: 'to-cyan-600', border: 'border-blue-400', name: 'Blue' },
  { from: 'from-emerald-600', to: 'to-green-600', border: 'border-emerald-400', name: 'Green' },
  { from: 'from-amber-600', to: 'to-orange-600', border: 'border-amber-400', name: 'Orange' },
  { from: 'from-rose-600', to: 'to-pink-600', border: 'border-rose-400', name: 'Pink' },
  { from: 'from-indigo-600', to: 'to-purple-600', border: 'border-indigo-400', name: 'Purple' },
  { from: 'from-teal-600', to: 'to-cyan-600', border: 'border-teal-400', name: 'Teal' },
  { from: 'from-fuchsia-600', to: 'to-purple-600', border: 'border-fuchsia-400', name: 'Fuchsia' },
  { from: 'from-lime-600', to: 'to-green-600', border: 'border-lime-400', name: 'Lime' }
];

export function DraggableClip({
  clip,
  version,
  versionIndex,
  sceneId,
  sceneStartTime,
  zoom,
  trackIndex,
  onClick
}: DraggableClipProps) {
  const ref = useRef<HTMLDivElement>(null);
  const relativeStart = clip.startTime - sceneStartTime;
  const width = clip.duration * zoom;
  const left = relativeStart * zoom;

  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.CLIP,
    item: { id: clip.id, versionId: version.id, sceneId, startTime: clip.startTime },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  drag(ref);

  const imageGens = version.generations?.filter((g: any) => g.type === 'image') || [];
  const videoGens = version.generations?.filter((g: any) => g.type === 'video') || [];
  
  // Get color scheme for this version
  const colorScheme = VERSION_COLORS[versionIndex % VERSION_COLORS.length];

  return (
    <div
      ref={ref}
      className="absolute h-12 cursor-move group"
      style={{
        left: `${left}px`,
        width: `${width}px`,
        top: `${trackIndex * 52}px`,
        opacity: isDragging ? 0.5 : 1
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick({ ...clip, selectedVersion: version });
      }}
    >
      <div className={`h-full bg-gradient-to-r ${colorScheme.from} ${colorScheme.to} rounded border ${colorScheme.border} flex items-center px-2 gap-2 shadow hover:shadow-lg transition-shadow`}>
        <GripHorizontal className="w-3 h-3 text-white/50 shrink-0" />
        
        <div className="flex-1 min-w-0 flex items-center gap-2">
          <span className="text-xs truncate flex-1">{version.imagePrompt}</span>
          
          <div className="flex gap-1 shrink-0">
            {imageGens.length > 0 && (
              <Badge className="bg-white/20 text-white text-xs h-4 px-1">
                <Image className="w-2.5 h-2.5 mr-0.5" />
                {imageGens.length}
              </Badge>
            )}
            {videoGens.length > 0 && (
              <Badge className="bg-white/20 text-white text-xs h-4 px-1">
                <Video className="w-2.5 h-2.5 mr-0.5" />
                {videoGens.length}
              </Badge>
            )}
          </div>
        </div>

        <Badge variant="outline" className="text-xs border-white/30 text-white shrink-0">
          V{version.id}
        </Badge>
      </div>
    </div>
  );
}
