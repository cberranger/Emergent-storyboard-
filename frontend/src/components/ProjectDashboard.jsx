import React, { useState, useEffect, useRef } from 'react';
import {
  Film, Music, Clock, Layers, Settings, Trash2, Edit,
  Play, Pause, Volume2, VolumeX, BarChart3, TrendingUp,
  Calendar, User
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/config';

const ProjectDashboard = ({ project, onProjectUpdate, onSceneSelect }) => {
  const [projectData, setProjectData] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const audioRef = useRef(null);

  // Settings form state
  const [settingsForm, setSettingsForm] = useState({
    name: '',
    description: '',
    music_file: ''
  });

  useEffect(() => {
    if (project?.id) {
      fetchProjectData();
      fetchScenes();
    }
  }, [project]);

  useEffect(() => {
    if (projectData) {
      setSettingsForm({
        name: projectData.name || '',
        description: projectData.description || '',
        music_file: projectData.music_file || ''
      });
    }
  }, [projectData]);

  const fetchProjectData = async () => {
    try {
      const response = await axios.get(`${API}/projects/${project.id}`);
      setProjectData(response.data);
    } catch (error) {
      console.error('Error fetching project:', error);
      toast.error('Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  const fetchScenes = async () => {
    try {
      const response = await axios.get(`${API}/projects/${project.id}/scenes`);
      setScenes(response.data);
    } catch (error) {
      console.error('Error fetching scenes:', error);
    }
  };

  const calculateStats = () => {
    const totalScenes = scenes.length;
    let totalClips = 0;
    let totalDuration = 0;

    scenes.forEach(scene => {
      if (scene.clips) {
        totalClips += scene.clips.length;
      }
      totalDuration += scene.duration || 0;
    });

    const completedScenes = scenes.filter(s => s.clips && s.clips.length > 0).length;
    const completionRate = totalScenes > 0 ? (completedScenes / totalScenes) * 100 : 0;

    return {
      totalScenes,
      totalClips,
      totalDuration,
      completionRate,
      completedScenes
    };
  };

  const handleUpdateSettings = async () => {
    try {
      await axios.put(`${API}/projects/${project.id}`, settingsForm);
      toast.success('Project settings updated');
      setShowSettings(false);
      fetchProjectData();
      if (onProjectUpdate) onProjectUpdate();
    } catch (error) {
      console.error('Error updating project:', error);
      toast.error('Failed to update project settings');
    }
  };

  const handleDeleteProject = async () => {
    try {
      await axios.delete(`${API}/projects/${project.id}`);
      toast.success('Project deleted');
      setShowDeleteConfirm(false);
      if (onProjectUpdate) onProjectUpdate();
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Failed to delete project');
    }
  };

  // Audio player controls
  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (value) => {
    const newVolume = value[0];
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (value) => {
    const newTime = value[0];
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-secondary">Loading project dashboard...</div>
      </div>
    );
  }

  const stats = calculateStats();

  return (
    <div className="h-full overflow-auto p-6 bg-gray-900">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-200">{projectData?.name}</h1>
            <p className="text-sm text-gray-400 mt-1">{projectData?.description}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(true)}
              className="border-gray-700 hover:bg-gray-800"
            >
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDeleteConfirm(true)}
              className="border-red-700 hover:bg-red-900 text-red-400"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Scenes</p>
                  <p className="text-3xl font-bold text-gray-200 mt-1">{stats.totalScenes}</p>
                </div>
                <Layers className="w-8 h-8 text-indigo-500" />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {stats.completedScenes} with clips
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Clips</p>
                  <p className="text-3xl font-bold text-gray-200 mt-1">{stats.totalClips}</p>
                </div>
                <Film className="w-8 h-8 text-purple-500" />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Across all scenes
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Duration</p>
                  <p className="text-3xl font-bold text-gray-200 mt-1">
                    {Math.floor(stats.totalDuration / 60)}m
                  </p>
                </div>
                <Clock className="w-8 h-8 text-blue-500" />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {stats.totalDuration.toFixed(1)}s total
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Completion</p>
                  <p className="text-3xl font-bold text-gray-200 mt-1">
                    {stats.completionRate.toFixed(0)}%
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
              <Progress value={stats.completionRate} className="mt-2 h-2" />
            </CardContent>
          </Card>
        </div>

        {/* Music Player */}
        {projectData?.music_file && (
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center text-gray-200">
                <Music className="w-5 h-5 mr-2" />
                Project Music
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <audio
                ref={audioRef}
                src={projectData.music_file}
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={() => setIsPlaying(false)}
              />

              {/* Waveform / Progress Bar */}
              <div className="space-y-2">
                <Slider
                  value={[currentTime]}
                  max={duration || 100}
                  step={0.1}
                  onValueChange={handleSeek}
                  className="cursor-pointer"
                />
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={togglePlayPause}
                    className="border-gray-700 hover:bg-gray-700"
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
                    onClick={toggleMute}
                    className="hover:bg-gray-700"
                  >
                    {isMuted ? (
                      <VolumeX className="w-4 h-4" />
                    ) : (
                      <Volume2 className="w-4 h-4" />
                    )}
                  </Button>

                  <div className="w-24">
                    <Slider
                      value={[volume]}
                      max={1}
                      step={0.01}
                      onValueChange={handleVolumeChange}
                      className="cursor-pointer"
                    />
                  </div>
                </div>

                <p className="text-xs text-gray-500">
                  {projectData.music_file.split('/').pop()}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Scenes List */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-gray-200">Scenes</CardTitle>
            <CardDescription className="text-gray-400">
              Click a scene to view details
            </CardDescription>
          </CardHeader>
          <CardContent>
            {scenes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No scenes yet. Create your first scene to get started.
              </div>
            ) : (
              <div className="space-y-2">
                {scenes.map((scene, index) => (
                  <div
                    key={scene.id}
                    className="flex items-center justify-between p-4 bg-gray-900 rounded-lg hover:bg-gray-750 transition-colors cursor-pointer"
                    onClick={() => onSceneSelect && onSceneSelect(scene)}
                  >
                    <div className="flex items-center space-x-4 flex-1">
                      <Badge variant="outline" className="text-gray-400 border-gray-600">
                        #{index + 1}
                      </Badge>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-200">{scene.name}</h4>
                        <p className="text-sm text-gray-400 line-clamp-1">
                          {scene.description || 'No description'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <div className="flex items-center">
                        <Film className="w-4 h-4 mr-1" />
                        {scene.clips?.length || 0} clips
                      </div>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {scene.duration?.toFixed(1) || 0}s
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Project Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm text-gray-400">Created</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center text-gray-200">
                <Calendar className="w-4 h-4 mr-2" />
                {projectData?.created_at
                  ? new Date(projectData.created_at).toLocaleDateString()
                  : 'Unknown'}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm text-gray-400">Last Updated</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center text-gray-200">
                <Clock className="w-4 h-4 mr-2" />
                {projectData?.updated_at
                  ? new Date(projectData.updated_at).toLocaleDateString()
                  : 'Unknown'}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="bg-gray-900 border-gray-700">
          <DialogHeader>
            <DialogTitle className="text-gray-200">Project Settings</DialogTitle>
            <DialogDescription className="text-gray-400">
              Update your project information
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 mb-2 block">Project Name</label>
              <Input
                value={settingsForm.name}
                onChange={(e) =>
                  setSettingsForm({ ...settingsForm, name: e.target.value })
                }
                className="bg-gray-800 border-gray-700 text-gray-200"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">Description</label>
              <Textarea
                value={settingsForm.description}
                onChange={(e) =>
                  setSettingsForm({ ...settingsForm, description: e.target.value })
                }
                className="bg-gray-800 border-gray-700 text-gray-200"
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">Music File URL</label>
              <Input
                value={settingsForm.music_file}
                onChange={(e) =>
                  setSettingsForm({ ...settingsForm, music_file: e.target.value })
                }
                className="bg-gray-800 border-gray-700 text-gray-200"
                placeholder="https://example.com/music.mp3"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowSettings(false)}
              className="border-gray-700 hover:bg-gray-800"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpdateSettings}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent className="bg-gray-900 border-gray-700">
          <DialogHeader>
            <DialogTitle className="text-gray-200">Delete Project?</DialogTitle>
            <DialogDescription className="text-gray-400">
              This action cannot be undone. This will permanently delete the project
              "{projectData?.name}" and all associated scenes and clips.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteConfirm(false)}
              className="border-gray-700 hover:bg-gray-800"
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteProject}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProjectDashboard;
