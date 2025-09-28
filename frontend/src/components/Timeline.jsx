import React, { useState, useEffect, useRef } from 'react';
import { Plus, Play, Pause, SkipBack, SkipForward, Upload, Image, Video, Wand2, Settings, Volume2, Clock, Edit3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import axios from 'axios';
import { useDrag, useDrop, DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import SceneManager from './SceneManager';
import GenerationDialog from './GenerationDialog';

// Auto-detect environment  
const isDevelopment = process.env.NODE_ENV === 'development';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 
  (isDevelopment ? 'http://localhost:8001' : window.location.origin);
const API = `${BACKEND_URL}/api`;

const ItemTypes = {
  CLIP: 'clip'
};

const DraggableClip = ({ clip, onMove, onEdit, onGenerate }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.CLIP,
    item: { id: clip.id, position: clip.timeline_position },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  const activeVersion = clip.versions.find(v => v.version_number === clip.active_version) || clip.versions[0];

  return (
    <div
      ref={drag}
      className={`clip-item relative p-3 min-w-32 h-20 flex flex-col justify-between ${
        isDragging ? 'opacity-50' : 'opacity-100'
      }`}
      style={{ 
        left: `${clip.timeline_position * 100}px`,
        width: `${clip.length * 100}px` 
      }}
      data-testid={`timeline-clip-${clip.id}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h4 className="text-xs font-medium text-white truncate">{clip.name}</h4>
          <p className="text-xs text-white/70 truncate">{clip.lyrics || 'No lyrics'}</p>
        </div>
        <div className="flex space-x-1 ml-2">
          {activeVersion?.image_url && (
            <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30 text-xs px-1 py-0">
              <Image className="w-2 h-2" />
            </Badge>
          )}
          {activeVersion?.video_url && (
            <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs px-1 py-0">
              <Video className="w-2 h-2" />
            </Badge>
          )}
        </div>
      </div>
      
      <div className="flex items-center justify-between text-xs text-white/60">
        <span>{clip.length}s</span>
        <div className="flex space-x-1">
          <button 
            onClick={(e) => { e.stopPropagation(); onEdit(clip); }}
            className="hover:text-white transition-colors"
            data-testid={`edit-clip-${clip.id}-btn`}
          >
            <Edit3 className="w-3 h-3" />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onGenerate(clip); }}
            className="hover:text-white transition-colors"
            data-testid={`generate-clip-${clip.id}-btn`}
          >
            <Wand2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
};

const TimelineTrack = ({ scenes, clips, onClipMove, onClipEdit, onClipGenerate }) => {
  const [, drop] = useDrop(() => ({
    accept: ItemTypes.CLIP,
    drop: (item, monitor) => {
      const offset = monitor.getClientOffset();
      const trackRect = document.getElementById('timeline-track').getBoundingClientRect();
      const newPosition = Math.max(0, (offset.x - trackRect.left) / 100);
      onClipMove(item.id, newPosition);
    },
  }));

  return (
    <div
      id="timeline-track"
      ref={drop}
      className="timeline-track relative h-24 overflow-hidden"
      data-testid="timeline-track"
    >
      {/* Time ruler */}
      <div className="absolute top-0 left-0 right-0 h-6 border-b border-gray-600 bg-gray-800">
        <div className="relative h-full">
          {Array.from({ length: 20 }, (_, i) => (
            <div
              key={i}
              className="absolute top-0 h-full border-l border-gray-600"
              style={{ left: `${i * 100}px` }}
            >
              <span className="absolute top-1 left-1 text-xs text-gray-400">{i}s</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Clips */}
      <div className="absolute top-6 left-0 right-0 bottom-0">
        {clips.map((clip) => (
          <DraggableClip
            key={clip.id}
            clip={clip}
            onMove={onClipMove}
            onEdit={onClipEdit}
            onGenerate={onClipGenerate}
          />
        ))}
      </div>
    </div>
  );
};

const Timeline = ({ project, comfyUIServers }) => {
  const [scenes, setScenes] = useState([]);
  const [activeScene, setActiveScene] = useState(null);
  const [clips, setClips] = useState([]);
  const [showSceneManager, setShowSceneManager] = useState(false);
  const [showGenerationDialog, setShowGenerationDialog] = useState(false);
  const [selectedClip, setSelectedClip] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [musicFile, setMusicFile] = useState(null);
  const [editingScene, setEditingScene] = useState(false);
  const [sceneEditData, setSceneEditData] = useState({ description: '', lyrics: '' });
  const audioRef = useRef(null);

  useEffect(() => {
    if (project?.id) {
      fetchScenes();
    }
  }, [project]);

  useEffect(() => {
    if (activeScene?.id) {
      fetchClips();
    }
  }, [activeScene]);

  const fetchScenes = async () => {
    try {
      const response = await axios.get(`${API}/projects/${project.id}/scenes`);
      setScenes(response.data);
      if (response.data.length > 0 && !activeScene) {
        setActiveScene(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching scenes:', error);
      toast.error('Failed to fetch scenes');
    }
  };

  const fetchClips = async () => {
    if (!activeScene?.id) return;
    
    try {
      const response = await axios.get(`${API}/scenes/${activeScene.id}/clips`);
      setClips(response.data);
    } catch (error) {
      console.error('Error fetching clips:', error);
      toast.error('Failed to fetch clips');
    }
  };

  const handleClipMove = async (clipId, newPosition) => {
    try {
      await axios.put(`${API}/clips/${clipId}/timeline-position`, newPosition, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      setClips(prevClips => 
        prevClips.map(clip => 
          clip.id === clipId 
            ? { ...clip, timeline_position: newPosition }
            : clip
        )
      );
      
      toast.success('Clip position updated');
    } catch (error) {
      console.error('Error updating clip position:', error);
      toast.error('Failed to update clip position');
    }
  };

  const handleClipEdit = (clip) => {
    setSelectedClip(clip);
    setShowSceneManager(true);
  };

  const handleClipGenerate = (clip) => {
    setSelectedClip(clip);
    setShowGenerationDialog(true);
  };

  const handleSceneUpdate = async () => {
    if (!activeScene?.id) return;
    
    try {
      await axios.put(`${API}/scenes/${activeScene.id}`, sceneEditData);
      
      // Update the local scene data
      setActiveScene(prev => ({
        ...prev,
        ...sceneEditData
      }));
      
      // Update scenes list
      setScenes(prevScenes =>
        prevScenes.map(scene =>
          scene.id === activeScene.id
            ? { ...scene, ...sceneEditData }
            : scene
        )
      );
      
      setEditingScene(false);
      toast.success('Scene updated successfully');
    } catch (error) {
      console.error('Error updating scene:', error);
      toast.error('Failed to update scene');
    }
  };

  const startEditingScene = () => {
    setSceneEditData({
      description: activeScene?.description || '',
      lyrics: activeScene?.lyrics || ''
    });
    setEditingScene(true);
  };

  const handleMusicUpload = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await axios.post(`${API}/projects/${project.id}/upload-music`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMusicFile(file);
      toast.success('Music uploaded successfully');
    } catch (error) {
      console.error('Error uploading music:', error);
      toast.error('Failed to upload music');
    }
  };

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const totalDuration = Math.max(...clips.map(c => c.timeline_position + c.length), 10);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="h-full flex flex-col bg-panel">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-panel">
          <div>
            <h1 className="text-2xl font-bold text-primary">{project.name}</h1>
            <p className="text-secondary">Timeline Editor</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <input
              type="file"
              accept="audio/*"
              onChange={(e) => e.target.files[0] && handleMusicUpload(e.target.files[0])}
              className="hidden"
              id="music-upload"
            />
            <Button
              variant="outline"
              onClick={() => document.getElementById('music-upload').click()}
              className="btn-secondary"
              data-testid="upload-music-btn"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Music
            </Button>
            
            <Button
              onClick={() => setShowSceneManager(true)}
              className="btn-primary"
              data-testid="manage-scenes-btn"
            >
              <Plus className="w-4 h-4 mr-2" />
              Manage Scenes
            </Button>
          </div>
        </div>

        {/* Scene Tabs */}
        {scenes.length > 0 && (
          <div className="flex items-center p-4 border-b border-panel bg-panel-dark">
            <Tabs value={activeScene?.id} onValueChange={(sceneId) => {
              const scene = scenes.find(s => s.id === sceneId);
              setActiveScene(scene);
            }} className="w-full">
              <TabsList className="bg-panel">
                {scenes.map((scene) => (
                  <TabsTrigger 
                    key={scene.id} 
                    value={scene.id}
                    className="data-[state=active]:bg-indigo-600"
                    data-testid={`scene-tab-${scene.id}`}
                  >
                    {scene.name}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>
        )}

        {/* Controls */}
        <div className="flex items-center justify-between p-4 bg-panel-dark border-b border-panel">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={togglePlayback}
              disabled={!musicFile}
              className="btn-secondary"
              data-testid="playback-btn"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            
            <Button variant="outline" size="sm" className="btn-secondary" disabled>
              <SkipBack className="w-4 h-4" />
            </Button>
            
            <Button variant="outline" size="sm" className="btn-secondary" disabled>
              <SkipForward className="w-4 h-4" />
            </Button>
            
            <div className="flex items-center text-sm text-secondary">
              <Clock className="w-4 h-4 mr-1" />
              {currentTime.toFixed(1)}s / {totalDuration}s
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {musicFile && (
              <div className="flex items-center text-sm text-secondary">
                <Volume2 className="w-4 h-4 mr-2" />
                {musicFile.name}
              </div>
            )}
            
            <Button variant="outline" size="sm" className="btn-secondary" disabled>
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Timeline */}
        <div className="flex-1 p-6">
          <div className="timeline-container p-4">
            {/* Scene Info Section */}
            {activeScene && (
              <div className="mb-6 p-4 bg-panel-dark rounded-lg border border-panel">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-primary">
                    {activeScene.name}
                  </h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={startEditingScene}
                    className="btn-secondary"
                    data-testid="edit-scene-btn"
                  >
                    <Edit3 className="w-4 h-4 mr-2" />
                    Edit Scene
                  </Button>
                </div>
                
                {editingScene ? (
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium text-secondary mb-2 block">
                        Scene Description
                      </Label>
                      <Textarea
                        className="form-input min-h-[80px]"
                        placeholder="Describe this scene..."
                        value={sceneEditData.description}
                        onChange={(e) => setSceneEditData({
                          ...sceneEditData,
                          description: e.target.value
                        })}
                        data-testid="scene-description-input"
                      />
                    </div>
                    
                    <div>
                      <Label className="text-sm font-medium text-secondary mb-2 block">
                        Lyrics for this Scene
                      </Label>
                      <Textarea
                        className="form-input min-h-[100px]"
                        placeholder="Enter the lyrics for this scene..."
                        value={sceneEditData.lyrics}
                        onChange={(e) => setSceneEditData({
                          ...sceneEditData,
                          lyrics: e.target.value
                        })}
                        data-testid="scene-lyrics-input"
                      />
                    </div>
                    
                    <div className="flex justify-end space-x-3">
                      <Button
                        variant="outline"
                        onClick={() => setEditingScene(false)}
                        className="btn-secondary"
                        data-testid="cancel-scene-edit-btn"
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleSceneUpdate}
                        className="btn-primary"
                        data-testid="save-scene-btn"
                      >
                        Save Changes
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div>
                      <Label className="text-xs text-secondary">Description</Label>
                      <p className="text-sm text-primary mt-1">
                        {activeScene.description || 'No description provided'}
                      </p>
                    </div>
                    
                    {activeScene.lyrics && (
                      <div>
                        <Label className="text-xs text-secondary">Scene Lyrics</Label>
                        <div className="text-sm text-primary mt-1 p-3 bg-panel rounded border border-panel whitespace-pre-wrap">
                          {activeScene.lyrics}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Timeline Header */}
            {activeScene && (
              <div className="mb-4">
                <h4 className="text-md font-medium text-primary mb-2">Timeline</h4>
              </div>
            )}
            
            {activeScene ? (
              <TimelineTrack
                scenes={scenes}
                clips={clips}
                onClipMove={handleClipMove}
                onClipEdit={handleClipEdit}
                onClipGenerate={handleClipGenerate}
              />
            ) : (
              <div className="text-center py-16">
                <h4 className="text-lg font-medium text-secondary mb-2">No active scene</h4>
                <p className="text-secondary mb-4">Create a scene to start adding clips</p>
                <Button
                  onClick={() => setShowSceneManager(true)}
                  className="btn-primary"
                  data-testid="create-first-scene-btn"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Scene
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Audio element for playback */}
        {musicFile && (
          <audio
            ref={audioRef}
            src={URL.createObjectURL(musicFile)}
            onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)}
            onEnded={() => setIsPlaying(false)}
          />
        )}

        {/* Dialogs */}
        <SceneManager
          open={showSceneManager}
          onOpenChange={setShowSceneManager}
          project={project}
          scenes={scenes}
          activeScene={activeScene}
          selectedClip={selectedClip}
          onScenesChange={fetchScenes}
          onClipsChange={fetchClips}
          onSetSelectedClip={setSelectedClip}
        />
        
        <GenerationDialog
          open={showGenerationDialog}
          onOpenChange={setShowGenerationDialog}
          clip={selectedClip}
          servers={comfyUIServers}
          onGenerated={fetchClips}
        />
      </div>
    </DndProvider>
  );
};

export default Timeline;