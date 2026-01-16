import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTabs,
  DialogTabsList,
  DialogTabsTrigger,
  DialogTabsContent
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Clock, Film, Image as ImageIcon, Video, User, Copy, ChevronLeft, ChevronRight, X, Eye } from 'lucide-react';
import { clipService, characterService } from '@/services';

const ClipDetailsDialog = ({
  open,
  onOpenChange,
  clip,
  scene,
  onClipUpdate
}) => {
  const [currentTab, setCurrentTab] = useState('details');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [characters, setCharacters] = useState([]);
  const [selectedVersion1, setSelectedVersion1] = useState(null);
  const [selectedVersion2, setSelectedVersion2] = useState(null);

  // Initialize edit form when clip changes
  useEffect(() => {
    if (clip) {
      setEditForm({
        name: clip.name,
        lyrics: clip.lyrics || '',
        length: clip.length,
        timeline_position: clip.timeline_position,
        image_prompt: clip.image_prompt || '',
        video_prompt: clip.video_prompt || ''
      });
      setSelectedVersion1(clip.active_version);
      setSelectedVersion2(clip.versions?.length > 1 ? clip.versions[1]?.version_number : clip.active_version);
    }
  }, [clip]);

  // Load characters for assignment
  useEffect(() => {
    if (open && scene?.project_id) {
      loadCharacters();
    }
  }, [open, scene?.project_id]);

  const loadCharacters = async () => {
    try {
      const data = await characterService.getCharacters(scene.project_id);
      setCharacters(data.characters || []);
    } catch (error) {
      console.error('Error loading characters:', error);
    }
  };

  const handleSave = async () => {
    try {
      await clipService.updateClip(clip.id, editForm);
      toast.success('Clip updated successfully');
      setIsEditing(false);
      if (onClipUpdate) onClipUpdate();
    } catch (error) {
      console.error('Error updating clip:', error);
      toast.error('Failed to update clip');
    }
  };

  const handleAssignCharacter = async (characterId) => {
    try {
      await clipService.assignCharacter(clip.id, characterId);
      toast.success('Character assigned successfully');
      if (onClipUpdate) onClipUpdate();
    } catch (error) {
      console.error('Error assigning character:', error);
      toast.error('Failed to assign character');
    }
  };

  const handleRemoveCharacter = async () => {
    try {
      await clipService.assignCharacter(clip.id, null);
      toast.success('Character removed');
      if (onClipUpdate) onClipUpdate();
    } catch (error) {
      console.error('Error removing character:', error);
      toast.error('Failed to remove character');
    }
  };

  const handleSelectContent = async (contentType, contentId) => {
    try {
      const params = {
        image_id: contentType === 'image' ? contentId : clip.selected_image_id,
        video_id: contentType === 'video' ? contentId : clip.selected_video_id
      };
      await clipService.selectClipContent(clip.id, params);
      toast.success('Content selected successfully');
      if (onClipUpdate) onClipUpdate();
    } catch (error) {
      console.error('Error selecting content:', error);
      toast.error('Failed to select content');
    }
  };

  const getVersionById = (versionId) => {
    return clip.versions?.find(v => v.id === versionId);
  };

  if (!clip) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="text-primary flex items-center justify-between">
            <span>Clip Details: {clip.name}</span>
            {!isEditing ? (
              <Button
                size="sm"
                onClick={() => setIsEditing(true)}
                className="btn-primary"
              >
                Edit Clip
              </Button>
            ) : (
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setIsEditing(false)}
                  className="btn-secondary"
                >
                  Cancel
                </Button>
                <Button size="sm" onClick={handleSave} className="btn-primary">
                  Save
                </Button>
              </div>
            )}
          </DialogTitle>
        </DialogHeader>

        <DialogTabs value={currentTab} onValueChange={setCurrentTab} className="w-full h-full">
          <DialogTabsList className="grid w-full grid-cols-6 bg-panel-dark">
            <DialogTabsTrigger value="details">Details</DialogTabsTrigger>
            <DialogTabsTrigger value="generation">Generation</DialogTabsTrigger>
            <DialogTabsTrigger value="versions">Versions</DialogTabsTrigger>
            <DialogTabsTrigger value="character">Character</DialogTabsTrigger>
            <DialogTabsTrigger value="history">History</DialogTabsTrigger>
            <DialogTabsTrigger value="metadata">Metadata</DialogTabsTrigger>
          </DialogTabsList>

          {/* Details Tab */}
          <DialogTabsContent value="details" className="flex-1 overflow-hidden">
            <div className="space-y-6 overflow-y-auto max-h-[60vh] p-4">
              {/* Basic Information */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary">Basic Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {isEditing ? (
                    <>
                      <div>
                        <Label className="text-secondary">Clip Name</Label>
                        <Input
                          className="form-input mt-2"
                          value={editForm.name}
                          onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-secondary">Length (seconds)</Label>
                          <Input
                            type="number"
                            step="0.1"
                            min="0.1"
                            className="form-input mt-2"
                            value={editForm.length}
                            onChange={(e) => setEditForm({ ...editForm, length: parseFloat(e.target.value) })}
                          />
                        </div>
                        <div>
                          <Label className="text-secondary">Timeline Position (seconds)</Label>
                          <Input
                            type="number"
                            step="0.1"
                            min="0"
                            className="form-input mt-2"
                            value={editForm.timeline_position}
                            onChange={(e) => setEditForm({ ...editForm, timeline_position: parseFloat(e.target.value) })}
                          />
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-indigo-400" />
                        <span className="text-sm text-secondary">Length:</span>
                        <span className="text-sm text-primary font-medium">{clip.length}s</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-indigo-400" />
                        <span className="text-sm text-secondary">Position:</span>
                        <span className="text-sm text-primary font-medium">{clip.timeline_position}s</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Lyrics/Script */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary">Lyrics / Script</CardTitle>
                </CardHeader>
                <CardContent>
                  {isEditing ? (
                    <Textarea
                      className="form-input min-h-[150px]"
                      value={editForm.lyrics}
                      onChange={(e) => setEditForm({ ...editForm, lyrics: e.target.value })}
                      placeholder="Enter lyrics or script for this clip..."
                    />
                  ) : (
                    <div className="text-primary whitespace-pre-wrap bg-panel p-4 rounded border border-panel min-h-[100px]">
                      {clip.lyrics || <span className="text-secondary">No lyrics or script</span>}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Image Prompt */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary flex items-center space-x-2">
                    <ImageIcon className="w-4 h-4" />
                    <span>Image Generation Prompt</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isEditing ? (
                    <Textarea
                      className="form-input min-h-[100px]"
                      value={editForm.image_prompt}
                      onChange={(e) => setEditForm({ ...editForm, image_prompt: e.target.value })}
                      placeholder="Enter image generation prompt..."
                    />
                  ) : (
                    <div className="text-primary whitespace-pre-wrap bg-panel p-4 rounded border border-panel min-h-[80px]">
                      {clip.image_prompt || <span className="text-secondary">No image prompt</span>}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Video Prompt */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary flex items-center space-x-2">
                    <Video className="w-4 h-4" />
                    <span>Video Generation Prompt</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isEditing ? (
                    <Textarea
                      className="form-input min-h-[100px]"
                      value={editForm.video_prompt}
                      onChange={(e) => setEditForm({ ...editForm, video_prompt: e.target.value })}
                      placeholder="Enter video generation prompt..."
                    />
                  ) : (
                    <div className="text-primary whitespace-pre-wrap bg-panel p-4 rounded border border-panel min-h-[80px]">
                      {clip.video_prompt || <span className="text-secondary">No video prompt</span>}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </DialogTabsContent>

          {/* Generation Tab */}
          <DialogTabsContent value="generation" className="flex-1 overflow-hidden">
            <div className="space-y-6 overflow-y-auto max-h-[60vh] p-4">
              {/* Generated Images */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary flex items-center space-x-2">
                    <ImageIcon className="w-4 h-4" />
                    <span>Generated Images</span>
                    <Badge variant="outline">{clip.generated_images?.length || 0}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {clip.generated_images && clip.generated_images.length > 0 ? (
                    <div className="grid grid-cols-3 gap-4">
                      {clip.generated_images.map((content) => (
                        <div key={content.id} className="relative group">
                          <img
                            src={content.url}
                            alt="Generated image"
                            className="w-full h-auto rounded border-2 border-transparent transition-all"
                            style={{
                              borderColor: clip.selected_image_id === content.id ? 'rgb(99, 102, 241)' : 'transparent'
                            }}
                          />
                          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-2">
                            <Button
                              size="sm"
                              onClick={() => handleSelectContent('image', content.id)}
                              className="btn-primary"
                              disabled={clip.selected_image_id === content.id}
                            >
                              {clip.selected_image_id === content.id ? 'Selected' : 'Select'}
                            </Button>
                            <Button size="sm" className="btn-secondary" asChild>
                              <a href={content.url} target="_blank" rel="noopener noreferrer">
                                <Eye className="w-4 h-4" />
                              </a>
                            </Button>
                          </div>
                          {clip.selected_image_id === content.id && (
                            <div className="absolute top-2 right-2">
                              <Badge className="bg-indigo-600">Selected</Badge>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-secondary">
                      No generated images yet
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Generated Videos */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary flex items-center space-x-2">
                    <Video className="w-4 h-4" />
                    <span>Generated Videos</span>
                    <Badge variant="outline">{clip.generated_videos?.length || 0}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {clip.generated_videos && clip.generated_videos.length > 0 ? (
                    <div className="grid grid-cols-2 gap-4">
                      {clip.generated_videos.map((content) => (
                        <div key={content.id} className="relative group">
                          <video
                            src={content.url}
                            controls
                            className="w-full h-auto rounded border-2 border-transparent transition-all"
                            style={{
                              borderColor: clip.selected_video_id === content.id ? 'rgb(99, 102, 241)' : 'transparent'
                            }}
                          />
                          <div className="absolute top-2 right-2">
                            {clip.selected_video_id === content.id && (
                              <Badge className="bg-indigo-600">Selected</Badge>
                            )}
                          </div>
                          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-2">
                            <Button
                              size="sm"
                              onClick={() => handleSelectContent('video', content.id)}
                              className="btn-primary"
                              disabled={clip.selected_video_id === content.id}
                            >
                              {clip.selected_video_id === content.id ? 'Selected' : 'Select'}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-secondary">
                      No generated videos yet
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </DialogTabsContent>

          {/* Versions Tab */}
          <DialogTabsContent value="versions" className="flex-1 overflow-hidden">
            <div className="space-y-6 overflow-y-auto max-h-[60vh] p-4">
              {/* Version Comparison */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary">Version Comparison</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-secondary mb-2 block">Version 1</Label>
                      <Select
                        value={selectedVersion1}
                        onValueChange={setSelectedVersion1}
                      >
                        <SelectTrigger className="form-input">
                          <SelectValue placeholder="Select version" />
                        </SelectTrigger>
                        <SelectContent>
                          {clip.versions?.map((version) => (
                            <SelectItem key={version.id} value={version.id}>
                              Version {version.version_number}
                              {clip.active_version === version.version_number && ' (Active)'}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label className="text-secondary mb-2 block">Version 2</Label>
                      <Select
                        value={selectedVersion2}
                        onValueChange={setSelectedVersion2}
                      >
                        <SelectTrigger className="form-input">
                          <SelectValue placeholder="Select version" />
                        </SelectTrigger>
                        <SelectContent>
                          {clip.versions?.map((version) => (
                            <SelectItem key={version.id} value={version.id}>
                              Version {version.version_number}
                              {clip.active_version === version.version_number && ' (Active)'}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {selectedVersion1 && selectedVersion2 && (
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      {/* Version 1 */}
                      <div className="space-y-4">
                        <div className="text-center">
                          <Badge className="bg-indigo-600 mb-2">
                            Version {getVersionById(selectedVersion1)?.version_number}
                          </Badge>
                        </div>
                        {getVersionById(selectedVersion1)?.image_url && (
                          <img
                            src={getVersionById(selectedVersion1).image_url}
                            alt={`Version ${getVersionById(selectedVersion1).version_number}`}
                            className="w-full h-auto rounded"
                          />
                        )}
                        {getVersionById(selectedVersion1)?.video_url && (
                          <video
                            src={getVersionById(selectedVersion1).video_url}
                            controls
                            className="w-full h-auto rounded"
                          />
                        )}
                        {getVersionById(selectedVersion1)?.image_prompt && (
                          <div className="text-sm text-secondary">
                            <span className="font-medium">Image Prompt:</span> {getVersionById(selectedVersion1).image_prompt}
                          </div>
                        )}
                        {getVersionById(selectedVersion1)?.video_prompt && (
                          <div className="text-sm text-secondary">
                            <span className="font-medium">Video Prompt:</span> {getVersionById(selectedVersion1).video_prompt}
                          </div>
                        )}
                      </div>

                      {/* Version 2 */}
                      <div className="space-y-4">
                        <div className="text-center">
                          <Badge className="bg-green-600 mb-2">
                            Version {getVersionById(selectedVersion2)?.version_number}
                          </Badge>
                        </div>
                        {getVersionById(selectedVersion2)?.image_url && (
                          <img
                            src={getVersionById(selectedVersion2).image_url}
                            alt={`Version ${getVersionById(selectedVersion2).version_number}`}
                            className="w-full h-auto rounded"
                          />
                        )}
                        {getVersionById(selectedVersion2)?.video_url && (
                          <video
                            src={getVersionById(selectedVersion2).video_url}
                            controls
                            className="w-full h-auto rounded"
                          />
                        )}
                        {getVersionById(selectedVersion2)?.image_prompt && (
                          <div className="text-sm text-secondary">
                            <span className="font-medium">Image Prompt:</span> {getVersionById(selectedVersion2).image_prompt}
                          </div>
                        )}
                        {getVersionById(selectedVersion2)?.video_prompt && (
                          <div className="text-sm text-secondary">
                            <span className="font-medium">Video Prompt:</span> {getVersionById(selectedVersion2).video_prompt}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* All Versions List */}
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary">All Versions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {clip.versions && clip.versions.length > 0 ? (
                      clip.versions.map((version) => (
                        <div
                          key={version.id}
                          className={`p-4 rounded border ${
                            clip.active_version === version.version_number
                              ? 'border-indigo-500 bg-indigo-500/10'
                              : 'border-panel'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Badge className={clip.active_version === version.version_number ? 'bg-indigo-600' : 'bg-panel-dark'}>
                                Version {version.version_number}
                              </Badge>
                              {clip.active_version === version.version_number && (
                                <Badge variant="outline">Active</Badge>
                              )}
                            </div>
                            <span className="text-sm text-secondary">
                              {new Date(version.created_at).toLocaleString()}
                            </span>
                          </div>
                          {version.image_url && (
                            <img
                              src={version.image_url}
                              alt={`Version ${version.version_number}`}
                              className="w-32 h-auto rounded mt-2"
                            />
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-secondary">
                        No versions created yet
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </DialogTabsContent>

          {/* Character Tab */}
          <DialogTabsContent value="character" className="flex-1 overflow-hidden">
            <div className="space-y-6 overflow-y-auto max-h-[60vh] p-4">
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary flex items-center space-x-2">
                    <User className="w-4 h-4" />
                    <span>Character Assignment</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {clip.character_id ? (
                    <div className="p-4 bg-indigo-500/10 border border-indigo-500 rounded">
                      <div>
                        <Label className="text-secondary mb-1 block">Assigned Character</Label>
                        <span className="text-primary font-medium">
                          {characters.find(c => c.id === clip.character_id)?.name || 'Unknown'}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-secondary">No character assigned</p>
                      <p className="text-sm text-secondary mt-2">Character assignment is managed through the Character Manager</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </DialogTabsContent>

          {/* History Tab */}
          <DialogTabsContent value="history" className="flex-1 overflow-hidden">
            <div className="space-y-6 overflow-y-auto max-h-[60vh] p-4">
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary">Generation History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* All generated content sorted by date */}
                    {clip.generated_images && clip.generated_images.length > 0 && (
                      <div className="space-y-3">
                        <Label className="text-secondary">Images</Label>
                        {clip.generated_images
                          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                          .map((content) => (
                            <div
                              key={content.id}
                              className="flex items-center space-x-4 p-3 bg-panel rounded border border-panel"
                            >
                              <img
                                src={content.url}
                                alt="Generated image"
                                className="w-20 h-20 rounded object-cover"
                              />
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-1">
                                  <span className="text-sm text-primary font-medium">
                                    {new Date(content.created_at).toLocaleString()}
                                  </span>
                                  {clip.selected_image_id === content.id && (
                                    <Badge className="bg-indigo-600 text-xs">Selected</Badge>
                                  )}
                                </div>
                                <div className="text-sm text-secondary">
                                  {content.server_name} - {content.model_name}
                                </div>
                                {content.prompt && (
                                  <div className="text-sm text-secondary mt-1 line-clamp-2">
                                    {content.prompt}
                                  </div>
                                )}
                              </div>
                              <Button
                                size="sm"
                                onClick={() => handleSelectContent('image', content.id)}
                                className="btn-primary"
                                disabled={clip.selected_image_id === content.id}
                              >
                                Select
                              </Button>
                            </div>
                          ))}
                      </div>
                    )}

                    {clip.generated_videos && clip.generated_videos.length > 0 && (
                      <div className="space-y-3">
                        <Label className="text-secondary">Videos</Label>
                        {clip.generated_videos
                          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                          .map((content) => (
                            <div
                              key={content.id}
                              className="flex items-center space-x-4 p-3 bg-panel rounded border border-panel"
                            >
                              <video
                                src={content.url}
                                className="w-20 h-20 rounded object-cover"
                              />
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-1">
                                  <span className="text-sm text-primary font-medium">
                                    {new Date(content.created_at).toLocaleString()}
                                  </span>
                                  {clip.selected_video_id === content.id && (
                                    <Badge className="bg-indigo-600 text-xs">Selected</Badge>
                                  )}
                                </div>
                                <div className="text-sm text-secondary">
                                  {content.server_name} - {content.model_name}
                                </div>
                                {content.prompt && (
                                  <div className="text-sm text-secondary mt-1 line-clamp-2">
                                    {content.prompt}
                                  </div>
                                )}
                              </div>
                              <Button
                                size="sm"
                                onClick={() => handleSelectContent('video', content.id)}
                                className="btn-primary"
                                disabled={clip.selected_video_id === content.id}
                              >
                                Select
                              </Button>
                            </div>
                          ))}
                      </div>
                    )}

                    {(!clip.generated_images || clip.generated_images.length === 0) &&
                     (!clip.generated_videos || clip.generated_videos.length === 0) && (
                      <div className="text-center py-8 text-secondary">
                        No generation history yet
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </DialogTabsContent>

          {/* Metadata Tab */}
          <DialogTabsContent value="metadata" className="flex-1 overflow-hidden">
            <div className="space-y-6 overflow-y-auto max-h-[60vh] p-4">
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-primary">Clip Metadata</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-secondary">Clip ID</Label>
                        <div className="text-sm text-primary font-mono mt-1">{clip.id}</div>
                      </div>
                      <div>
                        <Label className="text-secondary">Scene ID</Label>
                        <div className="text-sm text-primary font-mono mt-1">{clip.scene_id}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-secondary">Order</Label>
                        <div className="text-sm text-primary mt-1">{clip.order}</div>
                      </div>
                      <div>
                        <Label className="text-secondary">Active Version</Label>
                        <div className="text-sm text-primary mt-1">Version {clip.active_version}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-secondary">Total Versions</Label>
                        <div className="text-sm text-primary mt-1">{clip.versions?.length || 0}</div>
                      </div>
                      <div>
                        <Label className="text-secondary">Generated Images</Label>
                        <div className="text-sm text-primary mt-1">{clip.generated_images?.length || 0}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-secondary">Generated Videos</Label>
                        <div className="text-sm text-primary mt-1">{clip.generated_videos?.length || 0}</div>
                      </div>
                      <div>
                        <Label className="text-secondary">Character Assigned</Label>
                        <div className="text-sm text-primary mt-1">
                          {clip.character_id ? 'Yes' : 'No'}
                        </div>
                      </div>
                    </div>

                    <div>
                      <Label className="text-secondary">Created At</Label>
                      <div className="text-sm text-primary mt-1">
                        {new Date(clip.created_at).toLocaleString()}
                      </div>
                    </div>

                    <div>
                      <Label className="text-secondary">Updated At</Label>
                      <div className="text-sm text-primary mt-1">
                        {new Date(clip.updated_at).toLocaleString()}
                      </div>
                    </div>

                    {/* Generation Parameters (from selected content) */}
                    {(clip.selected_image_id || clip.selected_video_id) && (
                      <>
                        <div className="border-t border-panel pt-4">
                          <Label className="text-secondary mb-3 block">Current Generation Parameters</Label>
                          {clip.selected_image_id && (
                            <div className="bg-panel p-4 rounded border border-panel mb-4">
                              <div className="text-sm font-medium text-primary mb-2">Selected Image</div>
                              {clip.generated_images?.find(i => i.id === clip.selected_image_id)?.generation_params && (
                                <pre className="text-xs text-secondary overflow-x-auto">
                                  {JSON.stringify(
                                    clip.generated_images.find(i => i.id === clip.selected_image_id)?.generation_params,
                                    null,
                                    2
                                  )}
                                </pre>
                              )}
                            </div>
                          )}
                          {clip.selected_video_id && (
                            <div className="bg-panel p-4 rounded border border-panel">
                              <div className="text-sm font-medium text-primary mb-2">Selected Video</div>
                              {clip.generated_videos?.find(v => v.id === clip.selected_video_id)?.generation_params && (
                                <pre className="text-xs text-secondary overflow-x-auto">
                                  {JSON.stringify(
                                    clip.generated_videos.find(v => v.id === clip.selected_video_id)?.generation_params,
                                    null,
                                    2
                                  )}
                                </pre>
                              )}
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </DialogTabsContent>
        </DialogTabs>
      </DialogContent>
    </Dialog>
  );
};

export default ClipDetailsDialog;
