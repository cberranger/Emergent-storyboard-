import React, { useState, useEffect, useRef } from 'react';
import {
  Play, Pause, ZoomIn, ZoomOut, Plus, Settings, Music, Eye,
  ChevronDown, ChevronRight, Copy, Trash2, Wand2, Image as ImageIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/config';
import EnhancedGenerationDialog from './EnhancedGenerationDialog';

const UnifiedTimeline = ({ project, comfyUIServers }) => {
  const [timelineData, setTimelineData] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [selectedScene, setSelectedScene] = useState(null);
  const [selectedClip, setSelectedClip] = useState(null);
  const [expandedScenes, setExpandedScenes] = useState({});
  const [zoom, setZoom] = useState(10); // pixels per second
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showGenDialog, setShowGenDialog] = useState(false);
  const [genClip, setGenClip] = useState(null);
  const timelineRef = useRef(null);

  useEffect(() => {
    if (project?.id) {
      fetchTimelineData();
    }
  }, [project]);

  useEffect(() => {
    // Auto-select first scene and expand it
    if (scenes.length > 0 && !selectedScene) {
      const firstScene = scenes[0];
      setSelectedScene(firstScene);
      setExpandedScenes({ [firstScene.id]: true });
    }
  }, [scenes]);

  const fetchTimelineData = async () => {
    try {
      // Fetch scenes for this project
      const scenesResponse = await axios.get(`${API}/projects/${project.id}/scenes`);
      const scenesData = scenesResponse.data || [];

      // Fetch clips for each scene
      const scenesWithClips = await Promise.all(
        scenesData.map(async (scene) => {
          try {
            const clipsResponse = await axios.get(`${API}/scenes/${scene.id}/clips`);
            return { ...scene, clips: clipsResponse.data || [] };
          } catch (error) {
            console.error(`Error fetching clips for scene ${scene.id}:`, error);
            return { ...scene, clips: [] };
          }
        })
      );

      setScenes(scenesWithClips);
      setTimelineData({ scenes: scenesWithClips });
    } catch (error) {
      console.error('Error fetching timeline:', error);
      toast.error('Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  const toggleSceneExpansion = (sceneId) => {
    setExpandedScenes(prev => ({
      ...prev,
      [sceneId]: !prev[sceneId]
    }));
  };

  const handleSceneSelect = (scene) => {
    setSelectedScene(scene);
    if (!expandedScenes[scene.id]) {
      setExpandedScenes(prev => ({ ...prev, [scene.id]: true }));
    }
  };

  const handleClipSelect = (clip) => {
    setSelectedClip(clip);
  };

  const handleCreateSceneAlternate = async (sceneId) => {
    try {
      await axios.post(`${API}/scenes/${sceneId}/create-alternate`);
      toast.success('Scene alternate created');
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating scene alternate:', error);
      toast.error('Failed to create alternate');
    }
  };

  const handleCreateClipAlternate = async (clipId) => {
    try {
      await axios.post(`${API}/clips/${clipId}/create-alternate`);
      toast.success('Clip alternate created');
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating clip alternate:', error);
      toast.error('Failed to create alternate');
    }
  };

  const handleGenerateClip = (clip) => {
    setGenClip(clip);
    setShowGenDialog(true);
  };

  const calculateSceneDuration = (scene) => {
    if (!scene.clips || scene.clips.length === 0) return scene.duration || 10;
    const maxEnd = Math.max(...scene.clips.map(c => (c.timeline_position || 0) + (c.length || 5)));
    return Math.max(maxEnd, scene.duration || 10);
  };

  const calculateTotalDuration = () => {
    let totalDuration = 0;
    scenes.forEach(scene => {
      totalDuration += calculateSceneDuration(scene);
    });
    return Math.max(totalDuration, 60);
  };

  const getSceneColor = (scene) => {
    if (scene.is_alternate) {
      const colors = ['bg-slate-700', 'bg-slate-600', 'bg-slate-500'];
      return colors[scene.alternate_number % colors.length];
    }
    return 'bg-slate-800';
  };

  const getClipColor = (clip) => {
    if (clip.is_alternate) {
      const colors = ['bg-gray-600', 'bg-gray-500', 'bg-gray-400'];
      return colors[clip.alternate_number % colors.length];
    }
    return 'bg-gray-700';
  };

  const groupByParent = (items) => {
    const groups = {};
    items.forEach(item => {
      const parentId = item.parent_scene_id || item.parent_clip_id || item.id;
      if (!groups[parentId]) {
        groups[parentId] = [];
      }
      groups[parentId].push(item);
    });
    return Object.values(groups);
  };

  const getActiveItem = (group) => {
    // Return the first non-alternate, or first item
    return group.find(item => !item.is_alternate) || group[0];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-secondary">Loading timeline...</div>
      </div>
    );
  }

  const totalDuration = calculateTotalDuration();
  const sceneGroups = groupByParent(scenes);

  return (
    <div className="h-full flex bg-gray-900">
      {/* Main Timeline Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header Controls */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-950">
          <div className="flex items-center space-x-4">
            <h2 className="text-sm font-semibold text-gray-200">{project.name}</h2>
            <Badge variant="outline" className="text-xs">
              {scenes.length} scenes
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

            <Button variant="ghost" size="sm" onClick={() => setZoom(prev => Math.max(prev / 1.5, 2))} className="h-7 px-2">
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

            <Button variant="ghost" size="sm" onClick={() => setZoom(prev => Math.min(prev * 1.5, 50))} className="h-7 px-2">
              <ZoomIn className="w-4 h-4" />
            </Button>

            <span className="text-xs text-gray-400 ml-2">{zoom.toFixed(0)}px/s</span>
          </div>
        </div>

        {/* Three-Tier Timeline */}
        <div className="flex-1 overflow-auto" ref={timelineRef}>
          {/* Tier 1: Scene Preview Row */}
          <div className="border-b border-gray-800 bg-gray-950 p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs text-gray-400 font-medium">SCENES</span>
              <span className="text-xs text-gray-500">({sceneGroups.length})</span>
            </div>
            <div className="flex items-center space-x-3 overflow-x-auto pb-2">
              {sceneGroups.map((group, groupIndex) => {
                const activeScene = getActiveItem(group);
                const sceneDuration = calculateSceneDuration(activeScene);
                const clipCount = activeScene.clips?.length || 0;
                const isSelected = selectedScene?.id === activeScene.id;

                return (
                  <Card
                    key={activeScene.id}
                    className={`flex-shrink-0 cursor-pointer transition-all ${
                      isSelected
                        ? 'ring-2 ring-indigo-500 bg-indigo-500/10 border-indigo-500'
                        : 'bg-gray-800 border-gray-700 hover:border-gray-600'
                    }`}
                    style={{ width: '160px' }}
                    onClick={() => handleSceneSelect(activeScene)}
                  >
                    <CardContent className="p-3">
                      {/* Thumbnail Placeholder */}
                      <div className="aspect-video bg-gray-900 rounded mb-2 flex items-center justify-center">
                        <Play className="w-6 h-6 text-gray-600" />
                      </div>

                      {/* Scene Info */}
                      <div className="space-y-1">
                        <h4 className="text-xs font-medium text-gray-200 truncate">
                          {activeScene.name}
                        </h4>
                        <div className="flex items-center justify-between text-[10px] text-gray-400">
                          <span>{clipCount} clips</span>
                          <span>{sceneDuration.toFixed(1)}s</span>
                        </div>
                        {group.length > 1 && (
                          <Badge variant="secondary" className="text-[10px] h-4 px-1">
                            {group.length} versions
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}

              {/* Add Scene Button */}
              <Button
                variant="outline"
                size="sm"
                className="flex-shrink-0 h-32 w-32 border-dashed border-gray-700 hover:border-gray-600"
              >
                <div className="flex flex-col items-center">
                  <Plus className="w-6 h-6 mb-1" />
                  <span className="text-xs">Add Scene</span>
                </div>
              </Button>
            </div>
          </div>

          {/* Tier 2 & 3: Scene Timeline with Clips */}
          <div className="p-4 space-y-4">
            {sceneGroups.map((group, groupIndex) => {
              let currentPosition = 0;
              for (let i = 0; i < groupIndex; i++) {
                currentPosition += calculateSceneDuration(getActiveItem(sceneGroups[i]));
              }

              return group.map((scene, sceneIndex) => {
                const sceneDuration = calculateSceneDuration(scene);
                const isExpanded = expandedScenes[scene.id];
                const clipGroups = groupByParent(scene.clips || []);

                return (
                  <div key={scene.id} className="space-y-2">
                    {/* Scene Header */}
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleSceneExpansion(scene.id)}
                        className="h-6 px-1"
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </Button>

                      <div
                        className={`flex-1 h-10 rounded ${getSceneColor(scene)} border border-gray-700 px-3 flex items-center justify-between cursor-pointer hover:border-gray-600 transition-colors`}
                        style={{
                          marginLeft: `${sceneIndex * 4}px`
                        }}
                        onClick={() => handleSceneSelect(scene)}
                      >
                        <div className="flex items-center space-x-2 min-w-0 flex-1">
                          <span className="text-sm font-medium text-gray-200 truncate">
                            {scene.name}
                          </span>
                          {scene.is_alternate && (
                            <Badge variant="secondary" className="text-[10px] h-4 px-1">
                              A{scene.alternate_number}
                            </Badge>
                          )}
                          <span className="text-xs text-gray-400">
                            ({scene.clips?.length || 0} clips, {sceneDuration.toFixed(1)}s)
                          </span>
                        </div>

                        <div className="flex items-center space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCreateSceneAlternate(scene.id);
                            }}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </div>

                    {/* Expanded Clip Timeline */}
                    {isExpanded && (
                      <div className="ml-8 space-y-1 relative">
                        {/* Time Ruler for this scene */}
                        <div className="h-6 border-b border-gray-800 relative">
                          {Array.from({ length: Math.ceil(sceneDuration / 5) + 1 }).map((_, i) => {
                            const time = i * 5;
                            return (
                              <div
                                key={i}
                                className="absolute text-[10px] text-gray-500 font-mono"
                                style={{ left: `${time * zoom}px` }}
                              >
                                {time}s
                              </div>
                            );
                          })}
                        </div>

                        {/* Clips for this scene */}
                        <div className="relative">
                          {clipGroups.map((clipGroup, cgIndex) => {
                            return clipGroup.map((clip, clipIndex) => {
                              const clipStart = (clip.timeline_position || 0) * zoom;
                              const clipWidth = (clip.length || 5) * zoom;
                              const trackY = cgIndex * 50;
                              const isSelected = selectedClip?.id === clip.id;

                              return (
                                <div
                                  key={clip.id}
                                  className={`absolute h-12 rounded ${getClipColor(clip)} border ${
                                    isSelected ? 'border-indigo-500 ring-2 ring-indigo-500' : 'border-gray-600'
                                  } hover:border-gray-500 flex flex-col justify-between p-2 cursor-pointer transition-all`}
                                  style={{
                                    left: `${clipStart}px`,
                                    width: `${clipWidth}px`,
                                    top: `${trackY + clipIndex * 2}px`,
                                    minWidth: '60px'
                                  }}
                                  onClick={() => handleClipSelect(clip)}
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
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleGenerateClip(clip);
                                        }}
                                        className="h-4 w-4 p-0 hover:bg-gray-600"
                                      >
                                        <Wand2 className="w-3 h-3" />
                                      </Button>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleCreateClipAlternate(clip.id);
                                        }}
                                        className="h-4 w-4 p-0 hover:bg-gray-600"
                                      >
                                        <Copy className="w-3 h-3" />
                                      </Button>
                                    </div>
                                  </div>
                                </div>
                              );
                            });
                          })}
                        </div>

                        {/* Spacer for clips */}
                        <div style={{ height: `${Math.max(clipGroups.length * 50 + 20, 60)}px` }} />
                      </div>
                    )}
                  </div>
                );
              });
            })}
          </div>
        </div>
      </div>

      {/* Right Sidebar - Current Selection */}
      <div className="w-80 border-l border-gray-800 bg-gray-950 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-semibold text-gray-200">Current Selection</h3>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {selectedClip ? (
            <div className="space-y-4">
              {/* Clip Preview */}
              <div className="aspect-video bg-gray-900 rounded flex items-center justify-center">
                {selectedClip.generated_images?.length > 0 ? (
                  <img
                    src={selectedClip.generated_images[0].url}
                    alt={selectedClip.name}
                    className="w-full h-full object-cover rounded"
                  />
                ) : (
                  <Play className="w-12 h-12 text-gray-600" />
                )}
              </div>

              {/* Clip Info */}
              <div className="space-y-2">
                <h4 className="font-medium text-gray-200">{selectedClip.name}</h4>
                <p className="text-sm text-gray-400">
                  {selectedClip.image_prompt || 'No prompt yet'}
                </p>

                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <span>Length: {selectedClip.length}s</span>
                  <span>•</span>
                  <span>Position: {selectedClip.timeline_position || 0}s</span>
                </div>

                {selectedClip.generated_images?.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-xs text-gray-400">
                      {selectedClip.generated_images.length} generated image(s)
                    </span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <Button
                  className="w-full bg-indigo-600 hover:bg-indigo-700"
                  onClick={() => handleGenerateClip(selectedClip)}
                >
                  <Wand2 className="w-4 h-4 mr-2" />
                  Generate Content
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-gray-700 hover:bg-gray-800"
                  onClick={() => handleCreateClipAlternate(selectedClip.id)}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Create Alternate
                </Button>
              </div>
            </div>
          ) : selectedScene ? (
            <div className="space-y-4">
              <div className="aspect-video bg-gray-900 rounded flex items-center justify-center">
                <Play className="w-12 h-12 text-gray-600" />
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-gray-200">{selectedScene.name}</h4>
                <p className="text-sm text-gray-400">
                  {selectedScene.description || 'No description'}
                </p>

                <div className="text-xs text-gray-500">
                  {selectedScene.clips?.length || 0} clips • {calculateSceneDuration(selectedScene).toFixed(1)}s
                </div>
              </div>

              <Button
                variant="outline"
                className="w-full border-gray-700 hover:bg-gray-800"
                onClick={() => handleCreateSceneAlternate(selectedScene.id)}
              >
                <Copy className="w-4 h-4 mr-2" />
                Create Scene Alternate
              </Button>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <Eye className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Select a clip to preview generated content</p>
            </div>
          )}
        </div>
      </div>

      {/* Generation Dialog */}
      {showGenDialog && genClip && (
        <EnhancedGenerationDialog
          open={showGenDialog}
          onOpenChange={setShowGenDialog}
          clip={genClip}
          servers={comfyUIServers}
          onGenerated={fetchTimelineData}
        />
      )}
    </div>
  );
};

export default UnifiedTimeline;
