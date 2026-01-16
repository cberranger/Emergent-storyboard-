import React, { useState } from 'react';
import { Plus, Edit, Trash2, GripVertical, Clock, Film, Copy } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { sceneService, clipService } from '@/services';
import ClipDetailsDialog from './ClipDetailsDialog';

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

  // Drag and drop state for scenes
  const [draggedScene, setDraggedScene] = useState(null);
  const [dragOverScene, setDragOverScene] = useState(null);
  const [draggingScene, setDraggingScene] = useState(false);

  // Prompt templates state
  const [promptTemplates, setPromptTemplates] = useState([]);
  const [isCreatingTemplate, setIsCreatingTemplate] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    imagePrompt: '',
    videoPrompt: ''
  });

  // Clip details dialog state
  const [clipDetailsOpen, setClipDetailsOpen] = useState(false);
  const [selectedClipDetails, setSelectedClipDetails] = useState(null);

  const handleOpenClipDetails = (clip) => {
    setSelectedClipDetails(clip);
    setClipDetailsOpen(true);
  };

  const handleDragOver = (sceneId) => {
    setDragOverScene(sceneId);
  };

  const handleDragLeave = () => {
    setDragOverScene(null);
  };

  const handleDragStart = (e, sceneId) => {
    e.dataTransfer.setData('text/plain', JSON.stringify({ id: sceneId }));
    setDraggedScene(sceneId);
    setDraggingScene(true);
  };

  const handleSceneDrop = async (e) => {
    e.preventDefault();
    if (!draggedScene) return;

    // Get target scene ID from drop target
    const targetSceneId = e.currentTarget.dataset.sceneId;
    if (!targetSceneId) return;

    const fromIndex = scenes.findIndex(s => s.id === draggedScene);
    const toIndex = scenes.findIndex(s => s.id === targetSceneId);

    if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return;

    // Reorder scenes array
    const reorderedScenes = [...scenes];
    const [removedScene] = reorderedScenes.splice(fromIndex, 1);
    reorderedScenes.splice(toIndex, 0, removedScene);

    // Update scene order in backend
    const sceneOrderData = reorderedScenes.map((s, idx) => ({ id: s.id, order: idx }));
    await sceneService.updateSceneOrder(project.id, sceneOrderData);

    // Refresh scenes from parent
    onScenesChange();
    toast.success('Scene reordered successfully');

    // Clear drag state
    setDraggingScene(false);
    setDraggedScene(null);
    setDragOverScene(null);
  };

  // Prompt template handlers
  const handleCreateTemplate = () => {
    if (!newTemplate.name.trim()) return;
    const template = {
      id: Date.now().toString(),
      ...newTemplate
    };
    setPromptTemplates([...promptTemplates, template]);
    setNewTemplate({ name: '', imagePrompt: '', videoPrompt: '' });
    setIsCreatingTemplate(false);
    toast.success('Prompt template created');
  };

  const handleEditTemplate = (template) => {
    setEditingTemplate({ ...template });
  };

  const handleUpdateTemplate = () => {
    if (!editingTemplate.name.trim()) return;
    setPromptTemplates(promptTemplates.map(t =>
      t.id === editingTemplate.id ? editingTemplate : t
    ));
    setEditingTemplate(null);
    toast.success('Prompt template updated');
  };

  const handleDeleteTemplate = (templateId) => {
    setPromptTemplates(promptTemplates.filter(t => t.id !== templateId));
    toast.success('Prompt template deleted');
  };

  const handleApplyTemplate = async (template) => {
    if (!activeScene?.id) {
      toast.error('No active scene selected');
      return;
    }

    // Get all clips for the active scene
    const sceneClips = activeScene.clips || [];
    if (sceneClips.length === 0) {
      toast.error('Scene has no clips');
      return;
    }

    try {
      // Update all clips with template prompts
      for (const clip of sceneClips) {
        await clipService.updateClip(clip.id, {
          image_prompt: template.imagePrompt,
          video_prompt: template.videoPrompt
        });
      }

      onClipsChange();
      toast.success(`Applied template to ${sceneClips.length} clip(s)`);
    } catch (error) {
      console.error('Error applying template:', error);
      toast.error('Failed to apply template');
    }
  };

  // Scene Management
  const handleCreateScene = async (e) => {
    e.preventDefault();
    if (!newScene.name.trim()) return;
    
    try {
      await sceneService.createScene({
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
    }
  };

  const handleDuplicateScene = async (scene) => {
    try {
      // Create new scene with copied data
      const newScene = await sceneService.createScene({
        project_id: project.id,
        name: `${scene.name} (Copy)`,
        description: scene.description,
        lyrics: scene.lyrics,
        order: scenes.length
      });

      // Copy all clips from original scene
      if (scene.clips && scene.clips.length > 0) {
        for (const clip of scene.clips) {
          await clipService.createClip({
            scene_id: newScene.id,
            name: `${clip.name} (Copy)`,
            lyrics: clip.lyrics,
            length: clip.length,
            timeline_position: clip.timeline_position,
            image_prompt: clip.image_prompt,
            video_prompt: clip.video_prompt,
            order: clip.order
          });
        }
      }

      toast.success('Scene duplicated successfully');
      onScenesChange();
      onClipsChange();
    } catch (error) {
      console.error('Error duplicating scene:', error);
      toast.error('Failed to duplicate scene');
    }
  };

  const handleCreateClip = async (e) => {
    e.preventDefault();
    if (!newClip.name.trim() || !activeScene?.id) return;
    
    try {
      await clipService.createClip({
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
                    draggable
                    onDragStart={(e) => handleDragStart(e, scene.id)}
                    onDragOver={(e) => {
                      e.preventDefault();
                      handleDragOver(scene.id);
                    }}
                    onDrop={(e) => handleSceneDrop(e)}
                    onDragLeave={handleDragLeave}
                    data-scene-id={scene.id}
                    className={`glass-panel cursor-pointer transition-all ${
                      activeScene?.id === scene.id ? 'ring-2 ring-indigo-500' : ''
                    } ${
                      dragOverScene === scene.id ? 'ring-2 ring-indigo-300' : ''
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
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDuplicateScene(scene);
                            }}
                            className="btn-secondary"
                            title="Duplicate scene"
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
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
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-6">
                          <div className="flex items-center space-x-2 text-sm text-secondary">
                            <Clock className="w-4 h-4 mr-1" />
                            <span>{scene.clips?.length || 0} clips</span>
                          </div>
                          {scene.description && (
                            <div className="flex items-center space-x-2 text-sm text-secondary">
                              <Film className="w-4 h-4 mr-1" />
                              <span>{parseFloat(scene.duration || 0).toFixed(1)}s</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        {scene.description && (
                          <p className="text-sm text-secondary">{scene.description}</p>
                        )}
                      </div>
                      {scene.lyrics && (
                        <Label className="text-xs text-secondary">Scene Lyrics</Label>
                        <div className="text-sm text-primary mt-1 p-3 bg-panel rounded border border-panel whitespace-pre-wrap">
                          {scene.lyrics}
                        </div>
                      )}
                    </div>
                  </CardContent>
                 ))}
              </div>

              {/* Prompt Templates Section */}
              <div className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-primary">Prompt Templates</h3>
                  <Button
                    onClick={() => setIsCreatingTemplate(true)}
                    className="btn-primary"
                    size="sm"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    New Template
                  </Button>
                </div>

                {isCreatingTemplate && (
                  <Card className="glass-panel">
                    <CardHeader>
                      <CardTitle className="text-primary">Create Prompt Template</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <Input
                          className="form-input"
                          placeholder="Template name"
                          value={newTemplate.name}
                          onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                        />
                        <Textarea
                          className="form-input"
                          placeholder="Image generation prompt"
                          value={newTemplate.imagePrompt}
                          onChange={(e) => setNewTemplate({ ...newTemplate, imagePrompt: e.target.value })}
                          rows={2}
                        />
                        <Textarea
                          className="form-input"
                          placeholder="Video generation prompt"
                          value={newTemplate.videoPrompt}
                          onChange={(e) => setNewTemplate({ ...newTemplate, videoPrompt: e.target.value })}
                          rows={2}
                        />
                        <div className="flex justify-end space-x-2">
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                              setIsCreatingTemplate(false);
                              setNewTemplate({ name: '', imagePrompt: '', videoPrompt: '' });
                            }}
                            className="btn-secondary"
                          >
                            Cancel
                          </Button>
                          <Button onClick={handleCreateTemplate} className="btn-primary">
                            Create Template
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                <div className="space-y-2">
                  {promptTemplates.map((template) => (
                    <Card key={template.id} className="glass-panel">
                      <CardContent className="p-4">
                        {editingTemplate?.id === template.id ? (
                          <div className="space-y-3">
                            <Input
                              className="form-input"
                              value={editingTemplate.name}
                              onChange={(e) => setEditingTemplate({ ...editingTemplate, name: e.target.value })}
                              placeholder="Template name"
                            />
                            <Textarea
                              className="form-input"
                              value={editingTemplate.imagePrompt}
                              onChange={(e) => setEditingTemplate({ ...editingTemplate, imagePrompt: e.target.value })}
                              placeholder="Image prompt"
                              rows={2}
                            />
                            <Textarea
                              className="form-input"
                              value={editingTemplate.videoPrompt}
                              onChange={(e) => setEditingTemplate({ ...editingTemplate, videoPrompt: e.target.value })}
                              placeholder="Video prompt"
                              rows={2}
                            />
                            <div className="flex justify-end space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setEditingTemplate(null)}
                                className="btn-secondary"
                              >
                                Cancel
                              </Button>
                              <Button size="sm" onClick={handleUpdateTemplate} className="btn-primary">
                                Save
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div>
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <h4 className="font-medium text-primary mb-2">{template.name}</h4>
                                {template.imagePrompt && (
                                  <div className="text-sm text-secondary mb-2">
                                    <span className="text-xs font-medium">Image:</span> {template.imagePrompt}
                                  </div>
                                )}
                                {template.videoPrompt && (
                                  <div className="text-sm text-secondary">
                                    <span className="text-xs font-medium">Video:</span> {template.videoPrompt}
                                  </div>
                                )}
                              </div>
                              <div className="flex space-x-2 ml-4">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleApplyTemplate(template)}
                                  disabled={!activeScene}
                                  className="btn-primary"
                                  title="Apply to all clips in active scene"
                                >
                                  Apply
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleEditTemplate(template)}
                                  className="btn-secondary"
                                  title="Edit template"
                                >
                                  <Edit className="w-3 h-3" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleDeleteTemplate(template.id)}
                                  className="btn-secondary"
                                  title="Delete template"
                                >
                                  <Trash2 className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}

                  {promptTemplates.length === 0 && !isCreatingTemplate && (
                    <div className="text-center py-8 text-secondary">
                      No prompt templates yet. Create one to reuse prompts across clips.
                    </div>
                  )}
                </div>
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
                  <div className="flex space-x-2">
                    {selectedClip && (
                      <Button
                        onClick={() => handleOpenClipDetails(selectedClip)}
                        className="btn-primary"
                        variant="outline"
                      >
                        View Clip Details
                      </Button>
                    )}
                    <Button
                      onClick={() => setIsCreatingClip(true)}
                      className="btn-primary"
                      data-testid="create-clip-btn"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      New Clip
                    </Button>
                  </div>
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

                  {/* Clip Details Dialog */}
                  <ClipDetailsDialog
                    open={clipDetailsOpen}
                    onOpenChange={setClipDetailsOpen}
                    clip={selectedClipDetails}
                    scene={activeScene}
                    onClipUpdate={onClipsChange}
                  />
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