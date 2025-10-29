import React, { useState, useEffect, useRef } from 'react';
import {
  Play, Pause, ZoomIn, ZoomOut, Plus, Settings, Music, Eye,
  ChevronDown, ChevronRight, Copy, Trash2, Wand2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/config';
import EnhancedGenerationDialog from './EnhancedGenerationDialog';
import TimelineClipCard from './TimelineClipCard';

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
  const [showCreateClipDialog, setShowCreateClipDialog] = useState(false);
  const [createClipSceneId, setCreateClipSceneId] = useState(null);
  const [newClipData, setNewClipData] = useState({
    name: '',
    lyrics: '',
    length: 5,
    timeline_position: 0,
    image_prompt: '',
    video_prompt: ''
  });
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

  const handleCreateClip = async () => {
    if (!newClipData.name.trim() || !createClipSceneId) {
      toast.error('Clip name is required');
      return;
    }

    try {
      const response = await axios.post(`${API}/clips`, {
        scene_id: createClipSceneId,
        name: newClipData.name.trim(),
        lyrics: newClipData.lyrics.trim(),
        length: parseFloat(newClipData.length),
        timeline_position: parseFloat(newClipData.timeline_position),
        image_prompt: newClipData.image_prompt.trim(),
        video_prompt: newClipData.video_prompt.trim(),
        order: 0 // Will be recalculated on backend
      });

      toast.success('Clip created successfully');
      setShowCreateClipDialog(false);
      setCreateClipSceneId(null);
      setNewClipData({
        name: '',
        lyrics: '',
        length: 5,
        timeline_position: 0,
        image_prompt: '',
        video_prompt: ''
      });
      fetchTimelineData();
    } catch (error) {
      console.error('Error creating clip:', error);
      toast.error('Failed to create clip');
    }
  };

  const openCreateClipDialog = (sceneId) => {
    setCreateClipSceneId(sceneId);
    setShowCreateClipDialog(true);
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
      const colors = ['bg-slate-200', 'bg-slate-100', 'bg-gray-100'];
      return colors[scene.alternate_number % colors.length];
    }
    return 'bg-slate-300';
  };

  const getClipColor = (clip) => {
    if (clip.is_alternate) {
      const colors = ['bg-slate-400', 'bg-slate-300', 'bg-slate-200'];
      return colors[clip.alternate_number % colors.length];
    }
    return 'bg-slate-500';
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
    <div className="h-full flex bg-slate-50">
      {/* Main Timeline Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header Controls */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-white">
          <div className="flex items-center space-x-4">
            <h2 className="text-sm font-semibold text-slate-800">{project.name}</h2>
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

            <span className="text-xs text-slate-500 ml-2">{zoom.toFixed(0)}px/s</span>
          </div>
        </div>

        {/* Three-Tier Timeline */}
        <div className="flex-1 overflow-auto" ref={timelineRef}>
          {/* Tier 1: Scene Preview Row */}
          <div className="border-b border-slate-200 bg-white p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs text-slate-500 font-medium">SCENES</span>
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
                        : 'bg-slate-100 border-slate-300 hover:border-slate-400'
                    }`}
                    style={{ width: '160px' }}
                    onClick={() => handleSceneSelect(activeScene)}
                  >
                    <CardContent className="p-3">
                      {/* Thumbnail Placeholder */}
                      <div className="aspect-video bg-slate-100 rounded mb-2 flex items-center justify-center">
                        <Play className="w-6 h-6 text-gray-600" />
                      </div>

                      {/* Scene Info */}
                      <div className="space-y-1">
                        <h4 className="text-xs font-medium text-slate-800 truncate">
                          {activeScene.name}
                        </h4>
                        <div className="flex items-center justify-between text-[10px] text-slate-500">
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
                className="flex-shrink-0 h-32 w-32 border-dashed border-slate-300 hover:border-slate-400"
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
                        className={`flex-1 h-10 rounded ${getSceneColor(scene)} border border-slate-300 px-3 flex items-center justify-between cursor-pointer hover:border-slate-400 transition-colors`}
                        style={{
                          marginLeft: `${sceneIndex * 4}px`
                        }}
                        onClick={() => handleSceneSelect(scene)}
                      >
                        <div className="flex items-center space-x-2 min-w-0 flex-1">
                          <span className="text-sm font-medium text-slate-800 truncate">
                            {scene.name}
                          </span>
                          {scene.is_alternate && (
                            <Badge variant="secondary" className="text-[10px] h-4 px-1">
                              A{scene.alternate_number}
                            </Badge>
                          )}
                          <span className="text-xs text-slate-500">
                            ({scene.clips?.length || 0} clips, {sceneDuration.toFixed(1)}s)
                          </span>
                        </div>

                        <div className="flex items-center space-x-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              openCreateClipDialog(scene.id);
                            }}
                            className="h-6 px-2 text-xs"
                            title="Add new clip"
                          >
                            <Plus className="w-3 h-3 mr-1" />
                            Clip
                          </Button>
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
                        <div className="h-6 border-b border-slate-200 relative">
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
                                <TimelineClipCard
                                  key={clip.id}
                                  clip={clip}
                                  isSelected={selectedClip?.id === clip.id}
                                  zoom={zoom}
                                  trackY={trackY}
                                  clipIndex={clipIndex}
                                  onSelect={handleClipSelect}
                                  onGenerate={handleGenerateClip}
                                  onCreateAlternate={handleCreateClipAlternate}
                                  getClipColor={getClipColor}
                                />
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
      <div className="w-80 border-l border-slate-200 bg-white flex flex-col">
        <div className="p-4 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-gray-200">Current Selection</h3>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {selectedClip ? (
            <div className="space-y-4">
              {/* Clip Preview */}
              <div className="aspect-video bg-slate-100 rounded flex items-center justify-center">
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
              <div className="aspect-video bg-slate-100 rounded flex items-center justify-center">
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

      {/* Create Clip Dialog */}
      {showCreateClipDialog && (
        <Dialog open={showCreateClipDialog} onOpenChange={setShowCreateClipDialog}>
          <DialogContent className="bg-panel border-panel max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-primary">Create New Clip</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="clip-name">Clip Name *</Label>
                  <Input
                    id="clip-name"
                    value={newClipData.name}
                    onChange={(e) => setNewClipData({ ...newClipData, name: e.target.value })}
                    placeholder="Enter clip name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label htmlFor="clip-length">Length (s)</Label>
                    <Input
                      id="clip-length"
                      type="number"
                      min="1"
                      max="300"
                      step="0.1"
                      value={newClipData.length}
                      onChange={(e) => setNewClipData({ ...newClipData, length: parseFloat(e.target.value) || 5 })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="clip-position">Position (s)</Label>
                    <Input
                      id="clip-position"
                      type="number"
                      min="0"
                      step="0.1"
                      value={newClipData.timeline_position}
                      onChange={(e) => setNewClipData({ ...newClipData, timeline_position: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>
              </div>
              <div>
                <Label htmlFor="clip-lyrics">Lyrics/Script</Label>
                <Textarea
                  id="clip-lyrics"
                  value={newClipData.lyrics}
                  onChange={(e) => setNewClipData({ ...newClipData, lyrics: e.target.value })}
                  placeholder="Enter lyrics or script for this clip"
                  rows={3}
                />
              </div>
              <div>
                <Label htmlFor="clip-image-prompt">Image Prompt</Label>
                <Textarea
                  id="clip-image-prompt"
                  value={newClipData.image_prompt}
                  onChange={(e) => setNewClipData({ ...newClipData, image_prompt: e.target.value })}
                  placeholder="Describe the image to generate"
                  rows={2}
                />
              </div>
              <div>
                <Label htmlFor="clip-video-prompt">Video Prompt</Label>
                <Textarea
                  id="clip-video-prompt"
                  value={newClipData.video_prompt}
                  onChange={(e) => setNewClipData({ ...newClipData, video_prompt: e.target.value })}
                  placeholder="Describe the video to generate"
                  rows={2}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowCreateClipDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateClip}>
                  Create Clip
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default UnifiedTimeline;
