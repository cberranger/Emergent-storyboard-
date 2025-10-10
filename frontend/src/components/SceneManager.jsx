import React, { useState } from 'react';
import { Plus, Edit, Trash2, Film, Clock } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/config';

const SceneManager = ({ 
  open, 
  onOpenChange, 
  project, 
  scenes, 
  activeScene, 
  selectedClip, 
  onScenesChange, 
  onClipsChange,
  onSetSelectedClip
}) => {
  const [currentTab, setCurrentTab] = useState('scenes');
  const [isCreatingScene, setIsCreatingScene] = useState(false);
  const [isCreatingClip, setIsCreatingClip] = useState(false);
  const [editingScene, setEditingScene] = useState(null);
  const [editingClip, setEditingClip] = useState(null);
  
  const [newScene, setNewScene] = useState({ name: '', description: '', lyrics: '' });
  const [newClip, setNewClip] = useState({ 
    name: '', 
    lyrics: '', 
    length: 5, 
    timeline_position: 0,
    image_prompt: '',
    video_prompt: ''
  });

  // Scene Management
  const handleCreateScene = async (e) => {
    e.preventDefault();
    if (!newScene.name.trim()) return;
    
    try {
      await axios.post(`${API}/scenes`, {
        project_id: project.id,
        name: newScene.name,
        description: newScene.description,
        lyrics: newScene.lyrics,
        order: scenes.length
      });
      
      setNewScene({ name: '', description: '', lyrics: '' });
      setIsCreatingScene(false);
      onScenesChange();
      toast.success('Scene created successfully');
    } catch (error) {
      console.error('Error creating scene:', error);
      toast.error('Failed to create scene');
    }
  };

  const handleCreateClip = async (e) => {
    e.preventDefault();
    if (!newClip.name.trim() || !activeScene?.id) return;
    
    try {
      await axios.post(`${API}/clips`, {
        scene_id: activeScene.id,
        name: newClip.name,
        lyrics: newClip.lyrics,
        length: parseFloat(newClip.length),
        timeline_position: parseFloat(newClip.timeline_position),
        image_prompt: newClip.image_prompt,
        video_prompt: newClip.video_prompt,
        order: 0
      });
      
      setNewClip({ name: '', lyrics: '', length: 5, timeline_position: 0, image_prompt: '', video_prompt: '' });
      setIsCreatingClip(false);
      onClipsChange();
      toast.success('Clip created successfully');
    } catch (error) {
      console.error('Error creating clip:', error);
      toast.error('Failed to create clip');
    }
  };

  const startEditingClip = (clip) => {
    setEditingClip({ ...clip });
  };

  const handleUpdateClip = async () => {
    try {
      // For now, we'll just show a success message
      // In a full implementation, you'd have an update endpoint
      toast.success('Clip update functionality coming soon');
      setEditingClip(null);
    } catch (error) {
      toast.error('Failed to update clip');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-4xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="text-primary">Project Manager</DialogTitle>
        </DialogHeader>
        
        <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full h-full">
          <TabsList className="grid w-full grid-cols-2 bg-panel-dark">
            <TabsTrigger 
              value="scenes" 
              className="data-[state=active]:bg-indigo-600"
              data-testid="scenes-tab"
            >
              Scenes ({scenes.length})
            </TabsTrigger>
            <TabsTrigger 
              value="clips" 
              className="data-[state=active]:bg-indigo-600" 
              disabled={!activeScene}
              data-testid="clips-tab"
            >
              Clips {activeScene ? `(${activeScene.name})` : ''}
            </TabsTrigger>
          </TabsList>
          
          {/* Scenes Tab */}
          <TabsContent value="scenes" className="flex-1 overflow-hidden">
            <div className="space-y-4 h-full">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-primary">Scenes</h3>
                <Button 
                  onClick={() => setIsCreatingScene(true)} 
                  className="btn-primary"
                  data-testid="create-scene-btn"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Scene
                </Button>
              </div>
              
              {isCreatingScene && (
                <Card className="glass-panel">
                  <CardHeader>
                    <CardTitle className="text-primary">Create New Scene</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleCreateScene} className="space-y-4">
                      <Input
                        className="form-input"
                        placeholder="Scene name"
                        value={newScene.name}
                        onChange={(e) => setNewScene({ ...newScene, name: e.target.value })}
                        required
                        data-testid="scene-name-input"
                      />
                      <Textarea
                        className="form-input"
                        placeholder="Scene description"
                        value={newScene.description}
                        onChange={(e) => setNewScene({ ...newScene, description: e.target.value })}
                        data-testid="scene-description-input"
                      />
                      <Textarea
                        className="form-input min-h-[100px]"
                        placeholder="Lyrics for this scene"
                        value={newScene.lyrics}
                        onChange={(e) => setNewScene({ ...newScene, lyrics: e.target.value })}
                        data-testid="scene-lyrics-input"
                      />
                      <div className="flex justify-end space-x-2">
                        <Button 
                          type="button" 
                          variant="outline" 
                          onClick={() => setIsCreatingScene(false)}
                          className="btn-secondary"
                          data-testid="cancel-scene-btn"
                        >
                          Cancel
                        </Button>
                        <Button type="submit" className="btn-primary" data-testid="submit-scene-btn">
                          Create
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              )}
              
              <div className="space-y-3 overflow-y-auto max-h-96">
                {scenes.map((scene, index) => (
                  <Card 
                    key={scene.id} 
                    className={`glass-panel cursor-pointer transition-all ${
                      activeScene?.id === scene.id ? 'ring-2 ring-indigo-500' : ''
                    }`}
                    data-testid={`scene-card-${index}`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <Film className="w-4 h-4 text-indigo-400" />
                            <h4 className="font-medium text-primary">{scene.name}</h4>
                            {activeScene?.id === scene.id && (
                              <Badge variant="default" className="bg-indigo-600 text-xs">
                                Active
                              </Badge>
                            )}
                          </div>
                          {scene.description && (
                            <p className="text-sm text-secondary">{scene.description}</p>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="btn-secondary"
                            data-testid={`edit-scene-${index}-btn`}
                          >
                            <Edit className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>
          
          {/* Clips Tab */}
          <TabsContent value="clips" className="flex-1 overflow-hidden">
            {activeScene ? (
              <div className="space-y-4 h-full">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-primary">
                    Clips for "{activeScene.name}"
                  </h3>
                  <Button 
                    onClick={() => setIsCreatingClip(true)} 
                    className="btn-primary"
                    data-testid="create-clip-btn"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    New Clip
                  </Button>
                </div>
                
                {isCreatingClip && (
                  <Card className="glass-panel">
                    <CardHeader>
                      <CardTitle className="text-primary">Create New Clip</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <form onSubmit={handleCreateClip} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <Input
                            className="form-input"
                            placeholder="Clip name"
                            value={newClip.name}
                            onChange={(e) => setNewClip({ ...newClip, name: e.target.value })}
                            required
                            data-testid="clip-name-input"
                          />
                          <div className="flex space-x-2">
                            <Input
                              type="number"
                              step="0.1"
                              min="0.1"
                              className="form-input"
                              placeholder="Length (s)"
                              value={newClip.length}
                              onChange={(e) => setNewClip({ ...newClip, length: e.target.value })}
                              data-testid="clip-length-input"
                            />
                            <Input
                              type="number"
                              step="0.1"
                              min="0"
                              className="form-input"
                              placeholder="Position (s)"
                              value={newClip.timeline_position}
                              onChange={(e) => setNewClip({ ...newClip, timeline_position: e.target.value })}
                              data-testid="clip-position-input"
                            />
                          </div>
                        </div>
                        <Textarea
                          className="form-input"
                          placeholder="Lyrics or script"
                          value={newClip.lyrics}
                          onChange={(e) => setNewClip({ ...newClip, lyrics: e.target.value })}
                          data-testid="clip-lyrics-input"
                        />
                        <Textarea
                          className="form-input"
                          placeholder="Image generation prompt"
                          value={newClip.image_prompt}
                          onChange={(e) => setNewClip({ ...newClip, image_prompt: e.target.value })}
                          data-testid="clip-image-prompt-input"
                        />
                        <Textarea
                          className="form-input"
                          placeholder="Video generation prompt"
                          value={newClip.video_prompt}
                          onChange={(e) => setNewClip({ ...newClip, video_prompt: e.target.value })}
                          data-testid="clip-video-prompt-input"
                        />
                        <div className="flex justify-end space-x-2">
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => setIsCreatingClip(false)}
                            className="btn-secondary"
                            data-testid="cancel-clip-btn"
                          >
                            Cancel
                          </Button>
                          <Button type="submit" className="btn-primary" data-testid="submit-clip-btn">
                            Create
                          </Button>
                        </div>
                      </form>
                    </CardContent>
                  </Card>
                )}
                
                {/* Clip editing for selected clip */}
                {selectedClip && editingClip && editingClip.id === selectedClip.id && (
                  <Card className="glass-panel">
                    <CardHeader>
                      <CardTitle className="text-primary">Edit Clip: {selectedClip.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <Input
                            className="form-input"
                            placeholder="Clip name"
                            value={editingClip.name}
                            onChange={(e) => setEditingClip({ ...editingClip, name: e.target.value })}
                            data-testid="edit-clip-name-input"
                          />
                          <div className="flex space-x-2">
                            <Input
                              type="number"
                              step="0.1"
                              min="0.1"
                              className="form-input"
                              placeholder="Length (s)"
                              value={editingClip.length}
                              onChange={(e) => setEditingClip({ ...editingClip, length: parseFloat(e.target.value) })}
                              data-testid="edit-clip-length-input"
                            />
                            <div className="flex items-center text-sm text-secondary">
                              <Clock className="w-4 h-4 mr-1" />
                              {editingClip.timeline_position}s
                            </div>
                          </div>
                        </div>
                        <Textarea
                          className="form-input"
                          placeholder="Lyrics or script"
                          value={editingClip.lyrics}
                          onChange={(e) => setEditingClip({ ...editingClip, lyrics: e.target.value })}
                          data-testid="edit-clip-lyrics-input"
                        />
                        <div className="flex justify-end space-x-2">
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => setEditingClip(null)}
                            className="btn-secondary"
                            data-testid="cancel-edit-clip-btn"
                          >
                            Cancel
                          </Button>
                          <Button 
                            onClick={handleUpdateClip} 
                            className="btn-primary"
                            data-testid="save-clip-btn"
                          >
                            Save Changes
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <div className="text-center py-16">
                <h4 className="text-lg font-medium text-secondary mb-2">No active scene</h4>
                <p className="text-secondary">Select a scene to manage its clips</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default SceneManager;