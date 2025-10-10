import { useState } from 'react';
import { TimelineView } from './TimelineView';
import { SceneDetailsPanel } from './SceneDetailsPanel';
import { Button } from './ui/button';
import { Play, Pause, ZoomIn, ZoomOut, Plus } from 'lucide-react';

// Mock data structure
const mockProject = {
  id: 'project-1',
  name: 'kjk',
  duration: 120, // 2 minutes total
  scenes: [
    {
      id: 'scene-1',
      description: 'Opening scene with dramatic landscape',
      startTime: 0,
      duration: 30,
      currentVersion: 1,
      versions: [
        { id: 1, name: 'Version 1', thumbnail: '' },
        { id: 2, name: 'Version 2', thumbnail: '' }
      ],
      clips: [
        {
          id: 'clip-1',
          startTime: 0,
          duration: 5,
          imagePrompt: 'Dramatic mountain landscape at sunset, cinematic lighting',
          videoPrompt: 'Camera slowly pans across mountain range',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Dramatic mountain landscape at sunset, cinematic lighting',
              videoPrompt: 'Camera slowly pans across mountain range',
              generations: [
                { id: 'gen-1', type: 'image', url: '', status: 'completed' },
                { id: 'gen-2', type: 'video', url: '', status: 'completed' }
              ] 
            },
            { 
              id: 2, 
              name: 'Version 2',
              imagePrompt: 'Mountain range at golden hour, dramatic clouds',
              videoPrompt: 'Slow aerial pan revealing peaks',
              generations: [
                { id: 'gen-3', type: 'image', url: '', status: 'completed' }
              ] 
            },
            { 
              id: 3, 
              name: 'Version 3',
              imagePrompt: 'Epic mountain vista, storm clouds gathering',
              videoPrompt: 'Dynamic camera movement through clouds',
              generations: [] 
            }
          ],
          generations: [
            { id: 'gen-1', type: 'image', url: '', status: 'completed' },
            { id: 'gen-2', type: 'video', url: '', status: 'completed' }
          ]
        },
        {
          id: 'clip-2',
          startTime: 5,
          duration: 5,
          imagePrompt: 'Close-up of eagle soaring in sky',
          videoPrompt: 'Eagle wings spread, flying towards camera',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Close-up of eagle soaring in sky',
              videoPrompt: 'Eagle wings spread, flying towards camera',
              generations: [] 
            },
            { 
              id: 2, 
              name: 'Version 2',
              imagePrompt: 'Majestic eagle in flight, blue sky background',
              videoPrompt: 'Eagle soaring gracefully, wings outstretched',
              generations: [
                { id: 'gen-4', type: 'image', url: '', status: 'completed' }
              ] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-3',
          startTime: 10,
          duration: 5,
          imagePrompt: 'Forest clearing with mystical fog',
          videoPrompt: 'Fog swirls and parts revealing clearing',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Forest clearing with mystical fog',
              videoPrompt: 'Fog swirls and parts revealing clearing',
              generations: [] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-4',
          startTime: 15,
          duration: 5,
          imagePrompt: 'Ancient tree with glowing runes',
          videoPrompt: 'Camera orbits around the tree',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Ancient tree with glowing runes',
              videoPrompt: 'Camera orbits around the tree',
              generations: [] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-5',
          startTime: 20,
          duration: 5,
          imagePrompt: 'Mysterious portal opening',
          videoPrompt: 'Portal energy swirls and expands',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Mysterious portal opening',
              videoPrompt: 'Portal energy swirls and expands',
              generations: [] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-6',
          startTime: 25,
          duration: 5,
          imagePrompt: 'Hero stepping through portal',
          videoPrompt: 'Hero walks forward into light',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Hero stepping through portal',
              videoPrompt: 'Hero walks forward into light',
              generations: [] 
            }
          ],
          generations: []
        }
      ]
    },
    {
      id: 'scene-2',
      description: 'Character introduction sequence',
      startTime: 30,
      duration: 30,
      currentVersion: 1,
      versions: [{ id: 1, name: 'Version 1', thumbnail: '' }],
      clips: [
        {
          id: 'clip-7',
          startTime: 30,
          duration: 5,
          imagePrompt: 'Hooded figure standing in shadows',
          videoPrompt: 'Figure slowly turns toward camera',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Hooded figure standing in shadows',
              videoPrompt: 'Figure slowly turns toward camera',
              generations: [] 
            },
            { 
              id: 2, 
              name: 'Version 2',
              imagePrompt: 'Mysterious cloaked character in darkness',
              videoPrompt: 'Slow dramatic turn with cape flowing',
              generations: [] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-8',
          startTime: 35,
          duration: 5,
          imagePrompt: 'Close-up of mysterious eyes',
          videoPrompt: 'Eyes glow with magical energy',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Close-up of mysterious eyes',
              videoPrompt: 'Eyes glow with magical energy',
              generations: [] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-9',
          startTime: 40,
          duration: 5,
          imagePrompt: 'Hood falls back revealing face',
          videoPrompt: 'Dramatic reveal with wind effect',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Hood falls back revealing face',
              videoPrompt: 'Dramatic reveal with wind effect',
              generations: [] 
            }
          ],
          generations: []
        }
      ]
    },
    {
      id: 'scene-3',
      description: 'Action sequence in the city',
      startTime: 60,
      duration: 20,
      currentVersion: 1,
      versions: [{ id: 1, name: 'Version 1', thumbnail: '' }],
      clips: [
        {
          id: 'clip-10',
          startTime: 60,
          duration: 5,
          imagePrompt: 'Futuristic city skyline',
          videoPrompt: 'Camera flies through city',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Futuristic city skyline',
              videoPrompt: 'Camera flies through city',
              generations: [] 
            }
          ],
          generations: []
        },
        {
          id: 'clip-11',
          startTime: 65,
          duration: 5,
          imagePrompt: 'Chase scene on rooftops',
          videoPrompt: 'Characters running and jumping',
          currentVersion: 1,
          versions: [
            { 
              id: 1, 
              name: 'Version 1',
              imagePrompt: 'Chase scene on rooftops',
              videoPrompt: 'Characters running and jumping',
              generations: [] 
            }
          ],
          generations: []
        }
      ]
    }
  ]
};

export function TimelineEditor() {
  const [project, setProject] = useState(mockProject);
  const [zoom, setZoom] = useState(10); // pixels per second
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedScene, setSelectedScene] = useState<any>(null);
  const [selectedClip, setSelectedClip] = useState<any>(null);

  const handleSceneMove = (sceneId: string, newStartTime: number) => {
    setProject(prev => ({
      ...prev,
      scenes: prev.scenes.map(scene =>
        scene.id === sceneId
          ? {
              ...scene,
              startTime: Math.max(0, newStartTime),
              clips: scene.clips.map(clip => ({
                ...clip,
                startTime: clip.startTime - scene.startTime + Math.max(0, newStartTime)
              }))
            }
          : scene
      )
    }));
  };

  const handleClipMove = (sceneId: string, clipId: string, newStartTime: number) => {
    setProject(prev => ({
      ...prev,
      scenes: prev.scenes.map(scene =>
        scene.id === sceneId
          ? {
              ...scene,
              clips: scene.clips.map(clip =>
                clip.id === clipId
                  ? { ...clip, startTime: Math.max(scene.startTime, newStartTime) }
                  : clip
              )
            }
          : scene
      )
    }));
  };

  const handleAddScene = () => {
    const lastScene = project.scenes[project.scenes.length - 1];
    const newStartTime = lastScene ? lastScene.startTime + lastScene.duration : 0;
    
    const newScene = {
      id: `scene-${Date.now()}`,
      description: 'New scene',
      startTime: newStartTime,
      duration: 30,
      currentVersion: 1,
      versions: [{ id: 1, name: 'Version 1', thumbnail: '' }],
      clips: []
    };

    setProject(prev => ({
      ...prev,
      scenes: [...prev.scenes, newScene]
    }));
  };

  return (
    <div className="h-full flex flex-col bg-neutral-950">
      {/* Timeline Controls */}
      <div className="px-6 py-3 bg-neutral-900 border-b border-neutral-800 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <div className="text-sm text-neutral-400">
            {formatTime(currentTime)} / {formatTime(project.duration)}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-neutral-400">Zoom:</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setZoom(Math.max(5, zoom - 5))}
          >
            <ZoomOut className="w-4 h-4" />
          </Button>
          <span className="text-sm min-w-[4rem] text-center">{zoom}px/s</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setZoom(Math.min(50, zoom + 5))}
          >
            <ZoomIn className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Timeline View */}
      <div className="flex-1 overflow-auto">
        <TimelineView
          project={project}
          zoom={zoom}
          currentTime={currentTime}
          onSceneMove={handleSceneMove}
          onClipMove={handleClipMove}
          onSceneClick={setSelectedScene}
          onClipClick={setSelectedClip}
        />

        <div className="p-6">
          <Button
            variant="outline"
            className="w-full border-dashed border-neutral-700 hover:border-violet-500 hover:bg-violet-950/20"
            onClick={handleAddScene}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add New Scene
          </Button>
        </div>
      </div>

      {/* Details Panel */}
      <SceneDetailsPanel
        scene={selectedScene}
        clip={selectedClip}
        onClose={() => {
          setSelectedScene(null);
          setSelectedClip(null);
        }}
      />
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
