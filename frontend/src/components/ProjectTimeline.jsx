import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, ZoomIn, ZoomOut, Plus, Maximize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { projectService, sceneService, clipService } from '@/services';
import TimelineClipSimple from './TimelineClipSimple';
import SceneActionButtons from './SceneActionButtons';

const ProjectTimeline = ({ project, onSceneClick, onClipClick }) => {
  const [timelineData, setTimelineData] = useState(null);
  const [zoom, setZoom] = useState(10); // pixels per second
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isNewSceneDialogOpen, setIsNewSceneDialogOpen] = useState(false);
  const [newSceneName, setNewSceneName] = useState('');
  const [newSceneDescription, setNewSceneDescription] = useState('');
  const [newSceneLyrics, setNewSceneLyrics] = useState('');
  const [isNewClipDialogOpen, setIsNewClipDialogOpen] = useState(false);
  const [newClipSceneId, setNewClipSceneId] = useState(null);
  const [newClipName, setNewClipName] = useState('');
  const [newClipLyrics, setNewClipLyrics] = useState('');
  const [newClipLength, setNewClipLength] = useState(5.0);
  const [newClipTimelinePosition, setNewClipTimelinePosition] = useState(0.0);
  const timelineRef = useRef(null);
  const playheadRef = useRef(null);

  useEffect(() => {
    if (project?.id) {
      fetchTimelineData();
    }
  }, [project]);

  const fetchTimelineData = async () => {
    try {
      const data = await projectService.getProjectTimeline(project.id);
      setTimelineData(data);
    } catch (error) {
      console.error('Error fetching timeline:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateSceneDuration = (scene) => {
    if (!scene.clips || scene.clips.length === 0) return scene.duration || 10;
    const maxEnd = Math.max(...scene.clips.map(c => (c.timeline_position || 0) + (c.length || 5)));
    return Math.max(maxEnd, 10);
  };

  const calculateTotalDuration = () => {
    if (!timelineData?.scenes) return 60;
    let totalDuration = 0;
    timelineData.scenes.forEach(scene => {
      totalDuration += calculateSceneDuration(scene);
    });
    return Math.max(totalDuration, 60);
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.5, 100));
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.5, 2));

  const handleCreateAlternate = async (sceneId) => {
    try {
      await sceneService.createSceneAlternate(sceneId);
      toast.success('Scene alternate created');
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating alternate:', error);
    }
  };

  const handleCreateScene = async () => {
    if (!newSceneName.trim()) {
      toast.error('Scene name is required');
      return;
    }

    try {
      const order = timelineData?.scenes?.length || 0;
      await sceneService.createScene({
        project_id: project.id,
        name: newSceneName.trim(),
        description: newSceneDescription.trim(),
        lyrics: newSceneLyrics.trim(),
        order: order
      });
      toast.success('Scene created successfully');
      setIsNewSceneDialogOpen(false);
      setNewSceneName('');
      setNewSceneDescription('');
      setNewSceneLyrics('');
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating scene:', error);
      toast.error('Failed to create scene');
    }
  };

  const handleCreateClip = async () => {
    if (!newClipName.trim()) {
      toast.error('Clip name is required');
      return;
    }

    if (!newClipSceneId) {
      toast.error('No scene selected');
      return;
    }

    try {
      const scene = timelineData?.scenes?.find(s => s.id === newClipSceneId);
      const existingClips = scene?.clips || [];
      const order = existingClips.length;

      await clipService.createClip({
        scene_id: newClipSceneId,
        name: newClipName.trim(),
        lyrics: newClipLyrics.trim(),
        length: newClipLength,
        timeline_position: newClipTimelinePosition,
        order: order
      });
      toast.success('Clip created successfully');
      setIsNewClipDialogOpen(false);
      setNewClipSceneId(null);
      setNewClipName('');
      setNewClipLyrics('');
      setNewClipLength(5.0);
      setNewClipTimelinePosition(0.0);
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating clip:', error);
    }
  };

  const openNewClipDialog = (sceneId) => {
    setNewClipSceneId(sceneId);
    setIsNewClipDialogOpen(true);
  };

  const groupScenesByParent = (scenes) => {
    const groups = {};
    scenes.forEach(scene => {
      const parentId = scene.parent_scene_id || scene.id;
      if (!groups[parentId]) {
        groups[parentId] = [];
      }
      groups[parentId].push(scene);
    });
    return Object.values(groups);
  };

  const getSceneColor = (scene) => {
    if (scene.is_alternate) {
      const colors = ['bg-slate-200', 'bg-slate-100', 'bg-gray-100'];
      return colors[scene.alternate_number % colors.length];
    }
    return 'bg-slate-300';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-secondary">Loading timeline...</div>
      </div>
    );
  }

  const totalDuration = calculateTotalDuration();
  const sceneGroups = timelineData?.scenes ? groupScenesByParent(timelineData.scenes) : [];
  let currentPosition = 0;

  return (
    <div className="h-full flex flex-col bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-white">
        <div className="flex items-center space-x-4">
          <h2 className="text-sm font-semibold text-slate-800">{project.name} - Timeline</h2>
          <Badge variant="outline" className="text-xs">
            {timelineData?.scenes?.length || 0} scenes
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          <Dialog open={isNewSceneDialogOpen} onOpenChange={setIsNewSceneDialogOpen}>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="h-7 px-2"
              >
                <Plus className="w-4 h-4 mr-1" />
                New Scene
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Scene</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="scene-name">Scene Name *</Label>
                  <Input
                    id="scene-name"
                    value={newSceneName}
                    onChange={(e) => setNewSceneName(e.target.value)}
                    placeholder="Enter scene name"
                  />
                </div>
                <div>
                  <Label htmlFor="scene-description">Description</Label>
                  <Textarea
                    id="scene-description"
                    value={newSceneDescription}
                    onChange={(e) => setNewSceneDescription(e.target.value)}
                    placeholder="Enter scene description"
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="scene-lyrics">Lyrics</Label>
                  <Textarea
                    id="scene-lyrics"
                    value={newSceneLyrics}
                    onChange={(e) => setNewSceneLyrics(e.target.value)}
                    placeholder="Enter scene lyrics"
                    rows={4}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsNewSceneDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateScene}>
                    Create Scene
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={isNewClipDialogOpen} onOpenChange={setIsNewClipDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Clip</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="clip-name">Clip Name *</Label>
                  <Input
                    id="clip-name"
                    value={newClipName}
                    onChange={(e) => setNewClipName(e.target.value)}
                    placeholder="Enter clip name"
                  />
                </div>
                <div>
                  <Label htmlFor="clip-lyrics">Lyrics</Label>
                  <Textarea
                    id="clip-lyrics"
                    value={newClipLyrics}
                    onChange={(e) => setNewClipLyrics(e.target.value)}
                    placeholder="Enter clip lyrics"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="clip-length">Length (seconds)</Label>
                    <Input
                      id="clip-length"
                      type="number"
                      min="1"
                      max="300"
                      step="0.1"
                      value={newClipLength}
                      onChange={(e) => setNewClipLength(parseFloat(e.target.value) || 5.0)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="clip-position">Timeline Position (seconds)</Label>
                    <Input
                      id="clip-position"
                      type="number"
                      min="0"
                      step="0.1"
                      value={newClipTimelinePosition}
                      onChange={(e) => setNewClipTimelinePosition(parseFloat(e.target.value) || 0.0)}
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsNewClipDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateClip}>
                    Create Clip
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsPlaying(!isPlaying)}
            className="h-7 px-2"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>

          <div className="h-4 w-px bg-slate-300" />

          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomOut}
            className="h-7 px-2"
          >
            <ZoomOut className="w-4 h-4" />
          </Button>

          <div className="w-24">
            <Slider
              value={[zoom]}
              onValueChange={([value]) => setZoom(value)}
              min={2}
              max={50}
              step={1}
              className="cursor-pointer"
            />
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomIn}
            className="h-7 px-2"
          >
            <ZoomIn className="w-4 h-4" />
          </Button>

          <span className="text-xs text-slate-500 ml-2">{zoom.toFixed(0)}px/s</span>
        </div>
      </div>

      {/* Timeline Container */}
      <div className="flex-1 overflow-auto">
        <div ref={timelineRef} className="relative min-h-full">
          {/* Time Ruler */}
          <div className="sticky top-0 z-10 h-8 bg-white border-b border-slate-200 flex items-center">
            {Array.from({ length: Math.ceil(totalDuration / 5) + 1 }).map((_, i) => {
              const time = i * 5;
              return (
                <div
                  key={i}
                  className="absolute text-xs text-slate-500 font-mono"
                  style={{ left: `${time * zoom + 8}px` }}
                >
                  {time}s
                </div>
              );
            })}
          </div>

          {/* Playhead */}
          <div
            ref={playheadRef}
            className="absolute top-8 bottom-0 w-0.5 bg-red-500 z-20 pointer-events-none"
            style={{ left: `${currentTime * zoom + 8}px` }}
          >
            <div className="absolute -top-8 left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-8 border-l-transparent border-r-transparent border-t-red-500" />
          </div>

          {/* Scenes Track */}
          <div className="p-2 space-y-1">
            {sceneGroups.map((group, groupIndex) => {
              const originalScene = group.find(s => !s.is_alternate) || group[0];
              const sceneDuration = calculateSceneDuration(originalScene);
              const sceneStartPosition = currentPosition;
              currentPosition += sceneDuration;

              return (
                <div key={groupIndex} className="relative">
                  {/* Scene Group Stack */}
                  {group.map((scene, sceneIndex) => {
                    const clips = scene.clips || [];
                    const clipGroups = groupClipsByParent(clips);

                    return (
                      <div
                        key={scene.id}
                        className={`absolute ${getSceneColor(scene)} rounded border border-slate-300 hover:border-slate-400 transition-colors cursor-pointer overflow-hidden`}
                        style={{
                          left: `${sceneStartPosition * zoom}px`,
                          width: `${sceneDuration * zoom}px`,
                          top: `${sceneIndex * 2}px`,
                          height: `${Math.max(clips.length * 20 + 32, 60)}px`,
                          zIndex: group.length - sceneIndex
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSceneClick) onSceneClick(scene);
                        }}
                      >
                        {/* Scene Header */}
                        <div className="px-2 py-1 bg-slate-900/10 border-b border-slate-300 flex items-center justify-between">
                          <div className="flex items-center space-x-2 min-w-0 flex-1">
                            <span className="text-xs font-medium text-slate-800 truncate">
                              {scene.name}
                            </span>
                            {scene.is_alternate && (
                              <Badge variant="secondary" className="text-[10px] h-4 px-1">
                                A{scene.alternate_number}
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center space-x-1">
                            <SceneActionButtons
                              onAddClip={() => openNewClipDialog(scene.id)}
                              onCreateAlternate={() => handleCreateAlternate(scene.id)}
                            />
                          </div>
                        </div>

                        {/* Clips */}
                        <div className="relative p-1">
                          {clipGroups.map((clipGroup, cgIndex) => {
                            return clipGroup.map((clip, clipIndex) => {
                              const clipStart = (clip.timeline_position || 0) * zoom;
                              const clipWidth = (clip.length || 5) * zoom;
                              const trackY = cgIndex * 20;

                              return (
                                <TimelineClipSimple
                                  key={clip.id}
                                  clip={clip}
                                  zoom={zoom}
                                  trackY={trackY}
                                  clipIndex={clipIndex}
                                  onClick={onClipClick}
                                />
                              );
                            });
                          })}
                        </div>

                        {/* Spacer for clips */}
                        <div style={{ height: `${Math.max(clipGroups.length * 20 + 20, 40)}px` }} />
                      </div>
                    );
                  })}
                  <div style={{ height: `${Math.max(group.length * 2 + group[0].clips.length * 20 + 32, 70)}px` }} />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to group clips by parent
const groupClipsByParent = (clips) => {
  const groups = {};
  clips.forEach(clip => {
    const parentId = clip.parent_clip_id || clip.id;
    if (!groups[parentId]) {
      groups[parentId] = [];
    }
    groups[parentId].push(clip);
  });
  return Object.values(groups);
};

export default ProjectTimeline;
