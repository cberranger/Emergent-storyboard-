import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { DraggableScene } from './DraggableScene';
import { TimelineRuler } from './TimelineRuler';

interface TimelineViewProps {
  project: any;
  zoom: number;
  currentTime: number;
  onSceneMove: (sceneId: string, newStartTime: number) => void;
  onClipMove: (sceneId: string, clipId: string, newStartTime: number) => void;
  onSceneClick: (scene: any) => void;
  onClipClick: (clip: any) => void;
}

export function TimelineView({
  project,
  zoom,
  currentTime,
  onSceneMove,
  onClipMove,
  onSceneClick,
  onClipClick
}: TimelineViewProps) {
  const timelineWidth = project.duration * zoom;
  const playheadPosition = currentTime * zoom;

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="relative">
        {/* Timeline Ruler */}
        <TimelineRuler duration={project.duration} zoom={zoom} />

        {/* Timeline Content */}
        <div className="relative bg-neutral-900" style={{ minHeight: '300px' }}>
          {/* Playhead */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20 pointer-events-none"
            style={{ left: `${playheadPosition}px` }}
          >
            <div className="absolute -top-8 left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-8 border-l-transparent border-r-transparent border-t-red-500" />
          </div>

          {/* Grid lines */}
          <div className="absolute inset-0 pointer-events-none">
            {Array.from({ length: Math.ceil(project.duration / 5) }).map((_, i) => (
              <div
                key={i}
                className="absolute top-0 bottom-0 w-px bg-neutral-800"
                style={{ left: `${i * 5 * zoom}px` }}
              />
            ))}
          </div>

          {/* Scenes Track */}
          <div className="relative p-4 space-y-2">
            {project.scenes.map((scene: any) => (
              <DraggableScene
                key={scene.id}
                scene={scene}
                zoom={zoom}
                onMove={onSceneMove}
                onClipMove={onClipMove}
                onSceneClick={onSceneClick}
                onClipClick={onClipClick}
              />
            ))}
          </div>
        </div>
      </div>
    </DndProvider>
  );
}
