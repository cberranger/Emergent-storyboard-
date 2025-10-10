import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, Pause, ChevronLeft, ChevronRight, Maximize, X, Grid } from 'lucide-react';
import { useHotkeys } from '@/hooks/useHotkeys';

/**
 * Presentation Mode Component
 * Full-screen storyboard presentation with navigation and playback
 */
const PresentationMode = ({ project, scenes, clips, onClose }) => {
  const [currentSceneIndex, setCurrentSceneIndex] = useState(0);
  const [currentClipIndex, setCurrentClipIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [viewMode, setViewMode] = useState('single'); // 'single', 'scene', 'grid'
  const [autoPlayInterval, setAutoPlayInterval] = useState(null);

  // Get all clips in order
  const getAllClips = useCallback(() => {
    const allClips = [];
    scenes.forEach((scene, sceneIdx) => {
      const sceneClips = clips
        .filter(clip => clip.scene_id === scene.id)
        .sort((a, b) => a.order - b.order);
      sceneClips.forEach(clip => {
        allClips.push({ ...clip, sceneIndex: sceneIdx });
      });
    });
    return allClips;
  }, [scenes, clips]);

  const allClips = getAllClips();
  const currentClip = allClips[currentClipIndex];
  const currentScene = scenes[currentSceneIndex];

  // Navigation
  const goToNextClip = useCallback(() => {
    if (currentClipIndex < allClips.length - 1) {
      setCurrentClipIndex(prev => prev + 1);
      const nextClip = allClips[currentClipIndex + 1];
      if (nextClip) {
        setCurrentSceneIndex(nextClip.sceneIndex);
      }
    }
  }, [currentClipIndex, allClips]);

  const goToPreviousClip = useCallback(() => {
    if (currentClipIndex > 0) {
      setCurrentClipIndex(prev => prev - 1);
      const prevClip = allClips[currentClipIndex - 1];
      if (prevClip) {
        setCurrentSceneIndex(prevClip.sceneIndex);
      }
    }
  }, [currentClipIndex, allClips]);

  const goToNextScene = useCallback(() => {
    if (currentSceneIndex < scenes.length - 1) {
      const newSceneIndex = currentSceneIndex + 1;
      setCurrentSceneIndex(newSceneIndex);
      // Find first clip in new scene
      const firstClipIndex = allClips.findIndex(
        clip => clip.sceneIndex === newSceneIndex
      );
      if (firstClipIndex !== -1) {
        setCurrentClipIndex(firstClipIndex);
      }
    }
  }, [currentSceneIndex, scenes.length, allClips]);

  const goToPreviousScene = useCallback(() => {
    if (currentSceneIndex > 0) {
      const newSceneIndex = currentSceneIndex - 1;
      setCurrentSceneIndex(newSceneIndex);
      // Find first clip in new scene
      const firstClipIndex = allClips.findIndex(
        clip => clip.sceneIndex === newSceneIndex
      );
      if (firstClipIndex !== -1) {
        setCurrentClipIndex(firstClipIndex);
      }
    }
  }, [currentSceneIndex, allClips]);

  // Auto-play functionality
  useEffect(() => {
    if (isPlaying) {
      const duration = currentClip?.length || 5;
      const interval = setInterval(() => {
        if (currentClipIndex < allClips.length - 1) {
          goToNextClip();
        } else {
          setIsPlaying(false);
        }
      }, duration * 1000);
      setAutoPlayInterval(interval);
      return () => clearInterval(interval);
    } else if (autoPlayInterval) {
      clearInterval(autoPlayInterval);
      setAutoPlayInterval(null);
    }
  }, [isPlaying, currentClipIndex, currentClip, allClips.length, goToNextClip]);

  // Keyboard shortcuts
  const hotkeys = {
    'arrowright': goToNextClip,
    'arrowleft': goToPreviousClip,
    'arrowdown': goToNextScene,
    'arrowup': goToPreviousScene,
    ' ': () => setIsPlaying(!isPlaying),
    'escape': onClose,
    '1': () => setViewMode('single'),
    '2': () => setViewMode('scene'),
    '3': () => setViewMode('grid'),
    'f': () => {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        document.documentElement.requestFullscreen();
      }
    }
  };

  useHotkeys(hotkeys, [
    goToNextClip,
    goToPreviousClip,
    goToNextScene,
    goToPreviousScene,
    isPlaying,
    onClose
  ]);

  // Get display content for clip
  const getClipContent = (clip) => {
    // Try to get selected video first
    if (clip.selected_video_id && clip.generated_videos) {
      const selectedVideo = clip.generated_videos.find(
        v => v.id === clip.selected_video_id
      );
      if (selectedVideo) {
        return { type: 'video', url: selectedVideo.url };
      }
    }

    // Fall back to selected image
    if (clip.selected_image_id && clip.generated_images) {
      const selectedImage = clip.generated_images.find(
        i => i.id === clip.selected_image_id
      );
      if (selectedImage) {
        return { type: 'image', url: selectedImage.url };
      }
    }

    return null;
  };

  // Render single clip view
  const renderSingleView = () => {
    if (!currentClip) return null;
    const content = getClipContent(currentClip);

    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="max-w-6xl w-full">
          {/* Content */}
          <div className="aspect-video bg-black rounded-lg overflow-hidden mb-4">
            {content ? (
              content.type === 'video' ? (
                <video
                  src={content.url}
                  className="w-full h-full object-contain"
                  controls
                  autoPlay={isPlaying}
                />
              ) : (
                <img
                  src={content.url}
                  alt={currentClip.name}
                  className="w-full h-full object-contain"
                />
              )
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No content generated
              </div>
            )}
          </div>

          {/* Clip info */}
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">{currentClip.name}</h2>
            {currentClip.lyrics && (
              <p className="text-lg text-gray-300 mb-2">{currentClip.lyrics}</p>
            )}
            <p className="text-sm text-gray-400">
              Clip {currentClipIndex + 1} of {allClips.length} • Scene{' '}
              {currentSceneIndex + 1}: {currentScene?.name || 'Unnamed'}
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Render scene view (all clips in current scene)
  const renderSceneView = () => {
    const sceneClips = allClips.filter(
      clip => clip.sceneIndex === currentSceneIndex
    );

    return (
      <div className="p-8">
        <h2 className="text-3xl font-bold mb-6 text-center">
          Scene {currentSceneIndex + 1}: {currentScene?.name || 'Unnamed'}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {sceneClips.map((clip, idx) => {
            const content = getClipContent(clip);
            const clipGlobalIndex = allClips.findIndex(c => c.id === clip.id);
            const isActive = clipGlobalIndex === currentClipIndex;

            return (
              <Card
                key={clip.id}
                className={`cursor-pointer transition-all ${
                  isActive ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setCurrentClipIndex(clipGlobalIndex)}
              >
                <CardContent className="p-2">
                  <div className="aspect-video bg-black rounded overflow-hidden mb-2">
                    {content ? (
                      content.type === 'video' ? (
                        <video
                          src={content.url}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <img
                          src={content.url}
                          alt={clip.name}
                          className="w-full h-full object-cover"
                        />
                      )
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-xs text-gray-400">
                        No content
                      </div>
                    )}
                  </div>
                  <p className="text-sm font-medium truncate">{clip.name}</p>
                  <p className="text-xs text-gray-400 truncate">{clip.lyrics}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    );
  };

  // Render grid view (all clips)
  const renderGridView = () => {
    return (
      <div className="p-8">
        <h2 className="text-3xl font-bold mb-6 text-center">
          {project?.name || 'Project'} - Full Storyboard
        </h2>
        <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {allClips.map((clip, idx) => {
            const content = getClipContent(clip);
            const isActive = idx === currentClipIndex;

            return (
              <Card
                key={clip.id}
                className={`cursor-pointer transition-all ${
                  isActive ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => {
                  setCurrentClipIndex(idx);
                  setCurrentSceneIndex(clip.sceneIndex);
                  setViewMode('single');
                }}
              >
                <CardContent className="p-1">
                  <div className="aspect-video bg-black rounded overflow-hidden mb-1">
                    {content ? (
                      content.type === 'video' ? (
                        <video
                          src={content.url}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <img
                          src={content.url}
                          alt={clip.name}
                          className="w-full h-full object-cover"
                        />
                      )
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-xs text-gray-400">
                        No
                      </div>
                    )}
                  </div>
                  <p className="text-xs truncate">{clip.name}</p>
                  <p className="text-xs text-gray-400">S{clip.sceneIndex + 1}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Controls Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4 mr-2" />
            Exit
          </Button>
          <div className="text-sm text-gray-400">
            {project?.name || 'Presentation Mode'}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View mode buttons */}
          <Button
            variant={viewMode === 'single' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('single')}
            title="Single clip view (1)"
          >
            <Maximize className="w-4 h-4" />
          </Button>
          <Button
            variant={viewMode === 'scene' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('scene')}
            title="Scene view (2)"
          >
            Scene
          </Button>
          <Button
            variant={viewMode === 'grid' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
            title="Grid view (3)"
          >
            <Grid className="w-4 h-4" />
          </Button>

          <div className="w-px h-6 bg-gray-700 mx-2" />

          {/* Playback controls */}
          <Button
            variant="ghost"
            size="sm"
            onClick={goToPreviousClip}
            disabled={currentClipIndex === 0}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={goToNextClip}
            disabled={currentClipIndex === allClips.length - 1}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>

          <div className="w-px h-6 bg-gray-700 mx-2" />

          {/* Fullscreen */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              if (document.fullscreenElement) {
                document.exitFullscreen();
              } else {
                document.documentElement.requestFullscreen();
              }
            }}
            title="Fullscreen (F)"
          >
            <Maximize className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto">
        {viewMode === 'single' && renderSingleView()}
        {viewMode === 'scene' && renderSceneView()}
        {viewMode === 'grid' && renderGridView()}
      </div>

      {/* Progress indicator */}
      {viewMode === 'single' && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="bg-gray-900 bg-opacity-90 rounded-full px-4 py-2 text-sm">
            {currentClipIndex + 1} / {allClips.length}
          </div>
        </div>
      )}
    </div>
  );
};

export default PresentationMode;
