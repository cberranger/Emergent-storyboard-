import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, ZoomIn, ZoomOut, Plus, Maximize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/config';

const ProjectTimeline = ({ project, onSceneClick, onClipClick }) => {
  const [timelineData, setTimelineData] = useState(null);
  const [zoom, setZoom] = useState(10); // pixels per second
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);
  const timelineRef = useRef(null);
  const playheadRef = useRef(null);

  useEffect(() => {
    if (project?.id) {
      fetchTimelineData();
    }
  }, [project]);

  const fetchTimelineData = async () => {
    try {
      const response = await axios.get(`${API}/projects/${project.id}/timeline`);
      setTimelineData(response.data);
    } catch (error) {
      console.error('Error fetching timeline:', error);
      toast.error('Failed to load project timeline');
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
      await axios.post(`${API}/scenes/${sceneId}/create-alternate`);
      toast.success('Scene alternate created');
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating alternate:', error);
      toast.error('Failed to create alternate');
    }
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
      const colors = ['bg-slate-700', 'bg-slate-600', 'bg-slate-500'];
      return colors[scene.alternate_number % colors.length];
    }
    return 'bg-slate-800';
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
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-950">
        <div className="flex items-center space-x-4">
          <h2 className="text-sm font-semibold text-gray-200">{project.name} - Timeline</h2>
          <Badge variant="outline" className="text-xs">
            {timelineData?.scenes?.length || 0} scenes
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsPlaying(!isPlaying)}
            className="h-7 px-2"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>

          <div className="h-4 w-px bg-gray-700" />

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

          <span className="text-xs text-gray-400 ml-2">{zoom.toFixed(0)}px/s</span>
        </div>
      </div>

      {/* Timeline Container */}
      <div className="flex-1 overflow-auto">
        <div ref={timelineRef} className="relative min-h-full">
          {/* Time Ruler */}
          <div className="sticky top-0 z-10 h-8 bg-gray-950 border-b border-gray-800 flex items-center">
            {Array.from({ length: Math.ceil(totalDuration / 5) + 1 }).map((_, i) => {
              const time = i * 5;
              return (
                <div
                  key={i}
                  className="absolute text-xs text-gray-500 font-mono"
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
                        className={`absolute ${getSceneColor(scene)} rounded border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer overflow-hidden`}
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
                        <div className="px-2 py-1 bg-black/30 border-b border-gray-700 flex items-center justify-between">
                          <div className="flex items-center space-x-2 min-w-0 flex-1">
                            <span className="text-xs font-medium text-gray-200 truncate">
                              {scene.name}
                            </span>
                            {scene.is_alternate && (
                              <Badge variant="secondary" className="text-[10px] h-4 px-1">
                                A{scene.alternate_number}
                              </Badge>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCreateAlternate(scene.id);
                            }}
                            className="h-5 w-5 p-0 hover:bg-white/10"
                          >
                            <Plus className="w-3 h-3" />
                          </Button>
                        </div>

                        {/* Clips */}
                        <div className="relative p-1">
                          {clipGroups.map((clipGroup, cgIndex) => {
                            return clipGroup.map((clip, clipIndex) => {
                              const clipStart = (clip.timeline_position || 0) * zoom;
                              const clipWidth = (clip.length || 5) * zoom;
                              const trackY = cgIndex * 20;

                              return (
                                <div
                                  key={clip.id}
                                  className="absolute h-4 bg-gray-600 hover:bg-gray-500 rounded border border-gray-700 flex items-center px-1 cursor-pointer transition-colors"
                                  style={{
                                    left: `${clipStart}px`,
                                    width: `${clipWidth}px`,
                                    top: `${trackY + clipIndex}px`
                                  }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (onClipClick) onClipClick(clip);
                                  }}
                                >
                                  <span className="text-[10px] text-gray-200 truncate">
                                    {clip.name}
                                  </span>
                                  {clip.is_alternate && (
                                    <Badge variant="secondary" className="text-[8px] h-3 px-0.5 ml-1">
                                      A{clip.alternate_number}
                                    </Badge>
                                  )}
                                </div>
                              );
                            });
                          })}
                        </div>
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
