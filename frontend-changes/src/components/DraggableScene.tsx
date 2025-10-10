import { useRef } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { DraggableClip } from './DraggableClip';
import { Badge } from './ui/badge';
import { GripVertical } from 'lucide-react';

const ItemTypes = {
  SCENE: 'scene',
  CLIP: 'clip'
};

interface DraggableSceneProps {
  scene: any;
  zoom: number;
  onMove: (sceneId: string, newStartTime: number) => void;
  onClipMove: (sceneId: string, clipId: string, newStartTime: number) => void;
  onSceneClick: (scene: any) => void;
  onClipClick: (clip: any) => void;
}

export function DraggableScene({
  scene,
  zoom,
  onMove,
  onClipMove,
  onSceneClick,
  onClipClick
}: DraggableSceneProps) {
  const ref = useRef<HTMLDivElement>(null);
  const width = scene.duration * zoom;

  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.SCENE,
    item: { id: scene.id, startTime: scene.startTime },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    }),
    end: (item, monitor) => {
      const delta = monitor.getDifferenceFromInitialOffset();
      if (delta) {
        const newStartTime = Math.round((item.startTime + delta.x / zoom) / 5) * 5;
        onMove(scene.id, newStartTime);
      }
    }
  });

  const [, drop] = useDrop({
    accept: ItemTypes.CLIP,
    drop: (item: any, monitor) => {
      const delta = monitor.getDifferenceFromInitialOffset();
      if (delta && item.sceneId === scene.id) {
        const newStartTime = Math.round((item.startTime + delta.x / zoom));
        onClipMove(scene.id, item.id, newStartTime);
      }
    }
  });

  drag(drop(ref));

  // Calculate total height needed for all clip versions
  const getTotalClipHeight = (clips: any[]) => {
    const totalVersions = clips.reduce((sum, clip) => sum + clip.versions.length, 0);
    return totalVersions * 52 + 8; // 52px per track + 8px padding
  };

  return (
    <div
      ref={ref}
      className="absolute cursor-move group"
      style={{
        left: `${scene.startTime * zoom}px`,
        width: `${width}px`,
        opacity: isDragging ? 0.5 : 1
      }}
    >
      {/* Scene Block */}
      <div
        className="bg-gradient-to-r from-violet-600 to-purple-600 rounded-lg overflow-hidden border-2 border-violet-500 shadow-lg"
        onClick={(e) => {
          e.stopPropagation();
          onSceneClick(scene);
        }}
      >
        {/* Scene Header */}
        <div className="px-3 py-2 bg-black/30 flex items-center gap-2 border-b border-white/10">
          <GripVertical className="w-4 h-4 text-white/50" />
          <span className="text-sm flex-1 truncate">{scene.description}</span>
          <Badge variant="secondary" className="text-xs">
            {scene.duration}s
          </Badge>
          <Badge variant="outline" className="text-xs border-white/30 text-white">
            {scene.clips.length} clips
          </Badge>
        </div>

        {/* Clips Stack */}
        <div className="p-2 relative" style={{ minHeight: `${getTotalClipHeight(scene.clips)}px` }}>
          {scene.clips.map((clip: any, clipIndex: number) => {
            let trackOffset = 0;
            // Calculate track offset for this clip
            for (let i = 0; i < clipIndex; i++) {
              trackOffset += scene.clips[i].versions.length;
            }
            
            return clip.versions.map((version: any, versionIndex: number) => (
              <DraggableClip
                key={`${clip.id}-v${version.id}`}
                clip={clip}
                version={version}
                versionIndex={versionIndex}
                sceneId={scene.id}
                sceneStartTime={scene.startTime}
                zoom={zoom}
                trackIndex={trackOffset + versionIndex}
                onClick={onClipClick}
              />
            ));
          })}
        </div>
      </div>
    </div>
  );
}
