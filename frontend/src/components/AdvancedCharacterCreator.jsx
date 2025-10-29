import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/config';
import { toast } from 'sonner';
import {
  Users, Plus, Upload, Camera, Image as ImageIcon, 
  Settings, Play, Download, RefreshCw, Zap, Eye,
  User, Fullscreen, Grid3x3, Sparkles, Monitor, Server
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const AdvancedCharacterCreator = ({ activeProject, onCharacterCreated, comfyUIServers }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedServer, setSelectedServer] = useState('');
  const [uploadedImages, setUploadedImages] = useState({});
  const [generatedProfiles, setGeneratedProfiles] = useState([]);
  const [showProfiles, setShowProfiles] = useState(false);
  
  // Character data
  const [characterData, setCharacterData] = useState({
    name: '',
    description: '',
    generation_method: 'ip_adapter',
    trigger_words: '',
    style_notes: '',
    generation_params: {}
  });
  
  // Profile generation settings
  const [profileSettings, setProfileSettings] = useState({
    profile_type: 'comprehensive',
    pose_style: 'professional',
    controlnet_type: 'openpose',
    count: 4
  });

  useEffect(() => {
    if (comfyUIServers.length > 0 && !selectedServer) {
      setSelectedServer(comfyUIServers[0].id);
    }
  }, [comfyUIServers]);

  const handleImageUpload = async (file, type) => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('face_image', type === 'face' ? file : null);
      formData.append('full_body_image', type === 'body' ? file : null);
      
      if (type === 'reference' && file) {
        formData.append('reference_images', file);
      }
      
      const response = await axios.post(`${API}/upload-character-images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadedImages(prev => ({
        ...prev,
        ...response.data.files
      }));
      
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} image uploaded successfully`);
    } catch (error) {
      console.error('Error uploading image:', error);
      toast.error(`Failed to upload ${type} image`);
    } finally {
      setLoading(false);
    }
  };

  const createCharacter = async () => {
    if (!characterData.name.trim()) {
      toast.error('Character name is required');
      return;
    }

    try {
      setLoading(true);
      const characterPayload = {
        ...characterData,
        project_id: activeProject.id,
        reference_images: uploadedImages.reference_images || [],
        face_image: uploadedImages.face_image || '',
        full_body_image: uploadedImages.full_body_image || ''
      };

      const response = await axios.post(`${API}/characters`, characterPayload);
      const character = response.data;
      
      toast.success('Character created successfully');
      setIsOpen(false);
      resetForm();
      
      if (onCharacterCreated) {
        onCharacterCreated(character);
      }
      
      // Show profile generation dialog
      generateCharacterProfiles(character.id);
      
    } catch (error) {
      console.error('Error creating character:', error);
      toast.error('Failed to create character');
    } finally {
      setLoading(false);
    }
  };

  const generateCharacterProfiles = async (characterId) => {
    if (!selectedServer) {
      toast.error('Please select a generation server');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API}/generate-character-profiles`, {
        character_id: characterId,
        server_id: selectedServer,
        ...profileSettings
      });

      setGeneratedProfiles(response.data.profiles);
      setShowProfiles(true);
      toast.success(`Generated ${response.data.total_generated} character profiles`);
    } catch (error) {
      console.error('Error generating profiles:', error);
      toast.error('Failed to generate character profiles');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setCharacterData({
      name: '',
      description: '',
      generation_method: 'ip_adapter',
      trigger_words: '',
      style_notes: '',
      generation_params: {}
    });
    setUploadedImages({});
    setGeneratedProfiles([]);
    setShowProfiles(false);
  };

  const generationMethods = [
    {
      value: 'ip_adapter',
      label: 'IP-Adapter',
      description: 'Best for overall consistency using reference images',
      icon: ImageIcon,
      recommended: true
    },
    {
      value: 'reactor',
      label: 'Reactor Face Swap',
      description: 'Advanced face swapping for photorealistic results',
      icon: User,
      needs: 'face_image'
    },
    {
      value: 'instantid',
      label: 'InstantID',
      description: 'Pose-guided generation with face control',
      icon: Camera,
      needs: 'face_image'
    },
    {
      value: 'lora',
      label: 'Custom LoRA',
      description: 'Train custom character models (coming soon)',
      icon: Zap,
      disabled: true
    }
  ];

  const profileTypes = [
    {
      value: 'comprehensive',
      label: 'Comprehensive Portfolio',
      description: 'Complete character profile with multiple views'
    },
    {
      value: 'headshots',
      label: 'Professional Headshots',
      description: 'Focus on facial features and expressions'
    },
    {
      value: 'poses',
      label: 'Dynamic Poses',
      description: 'Character in various action and casual poses'
    },
    {
      value: 'expressions',
      label: 'Expression Gallery',
      description: 'Range of emotions and facial expressions'
    }
  ];

  const controlnetTypes = [
    {
      value: 'openpose',
      label: 'OpenPose',
      description: 'Skeletal pose control for consistent body positioning'
    },
    {
      value: 'depth',
      label: 'Depth Map',
      description: '3D depth control for spatial consistency'
    },
    {
      value: 'canny',
      label: 'Canny Edge',
      description: 'Edge detection for structural control'
    }
  ];

  const poseStyles = [
    { value: 'professional', label: 'Professional', icon: '💼' },
    { value: 'casual', label: 'Casual', icon: '👕' },
    { value: 'action', label: 'Action', icon: '🏃' },
    { value: 'formal', label: 'Formal', icon: '🤵' }
  ];

  return (
    <>
      <Button onClick={() => setIsOpen(true)} className="gap-2">
        <Plus className="w-4 h-4" />
        Advanced Character Creator
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Advanced Character Creator
            </DialogTitle>
            <DialogDescription>
              Create professional characters using industry-standard AI workflows
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="basics" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="basics">Basic Info</TabsTrigger>
              <TabsTrigger value="images">Images</TabsTrigger>
              <TabsTrigger value="method">Generation Method</TabsTrigger>
              <TabsTrigger value="profiles">Profile Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="basics" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Character Name *</Label>
                  <Input
                    id="name"
                    value={characterData.name}
                    onChange={(e) => setCharacterData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Sarah Chen, Marcus Wright"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="trigger">Trigger Words</Label>
                  <Input
                    id="trigger"
                    value={characterData.trigger_words}
                    onChange={(e) => setCharacterData(prev => ({ ...prev, trigger_words: e.target.value }))}
                    placeholder="e.g., sarah_chen, brown_hair, glasses"
                  />
                  <p className="text-xs text-secondary">
                    Keywords to activate character in prompts
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Character Description</Label>
                <Textarea
                  id="description"
                  value={characterData.description}
                  onChange={(e) => setCharacterData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe appearance, personality, age, ethnicity, distinguishing features..."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="style">Style Notes</Label>
                <Textarea
                  id="style"
                  value={characterData.style_notes}
                  onChange={(e) => setCharacterData(prev => ({ ...prev, style_notes: e.target.value }))}
                  placeholder="Preferred art style, lighting, mood, consistent elements..."
                  rows={2}
                />
              </div>
            </TabsContent>

            <TabsContent value="images" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Face Image Upload */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Face Image
                    </CardTitle>
                    <CardDescription>
                      Clear front-facing photo for face-based methods
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {uploadedImages.face_image ? (
                        <div className="aspect-square rounded-lg overflow-hidden border">
                          <img
                            src={`${API}${uploadedImages.face_image}`}
                            alt="Face"
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ) : (
                        <div className="aspect-square rounded-lg border-2 border-dashed border-panel flex flex-col items-center justify-center">
                          <Upload className="w-8 h-8 text-secondary mb-2" />
                          <p className="text-sm text-secondary">No face image</p>
                        </div>
                      )}
                      <Input
                        type="file"
                        accept="image/*"
                        onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'face')}
                        className="cursor-pointer"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Full Body Image */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Fullscreen className="w-4 h-4" />
                      Full Body Image
                    </CardTitle>
                    <CardDescription>
                      Full-length shot for body consistency
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {uploadedImages.full_body_image ? (
                        <div className="aspect-square rounded-lg overflow-hidden border">
                          <img
                            src={`${API}${uploadedImages.full_body_image}`}
                            alt="Full body"
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ) : (
                        <div className="aspect-square rounded-lg border-2 border-dashed border-panel flex flex-col items-center justify-center">
                          <Camera className="w-8 h-8 text-secondary mb-2" />
                          <p className="text-sm text-secondary">No body image</p>
                        </div>
                      )}
                      <Input
                        type="file"
                        accept="image/*"
                        onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'body')}
                        className="cursor-pointer"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Reference Images */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Grid3x3 className="w-4 h-4" />
                      Reference Images
                    </CardTitle>
                    <CardDescription>
                      Multiple reference angles and styles
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {uploadedImages.reference_images && uploadedImages.reference_images.length > 0 ? (
                        <div className="grid grid-cols-2 gap-2">
                          {uploadedImages.reference_images.slice(0, 4).map((img, idx) => (
                            <div key={idx} className="aspect-square rounded overflow-hidden border">
                              <img
                                src={`${API}${img}`}
                                alt={`Reference ${idx + 1}`}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          ))}
                          {uploadedImages.reference_images.length > 4 && (
                            <div className="aspect-square rounded border flex items-center justify-center">
                              <span className="text-xs text-secondary">
                                +{uploadedImages.reference_images.length - 4}
                              </span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="aspect-square rounded-lg border-2 border-dashed border-panel flex flex-col items-center justify-center">
                          <ImageIcon className="w-8 h-8 text-secondary mb-2" />
                          <p className="text-sm text-secondary">No references</p>
                        </div>
                      )}
                      <Input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={(e) => {
                          if (e.target.files.length > 0) {
                            Array.from(e.target.files).forEach(file => 
                              handleImageUpload(file, 'reference')
                            );
                          }
                        }}
                        className="cursor-pointer"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="method" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {generationMethods.map((method) => (
                  <Card 
                    key={method.value}
                    className={`cursor-pointer transition-all ${
                      characterData.generation_method === method.value 
                        ? 'ring-2 ring-primary border-primary' 
                        : 'hover:border-primary/50'
                    } ${method.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={() => !method.disabled && setCharacterData(prev => ({ ...prev, generation_method: method.value }))}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <method.icon className="w-4 h-4" />
                        {method.label}
                        {method.recommended && <Badge variant="default" className="text-xs">Recommended</Badge>}
                        {method.disabled && <Badge variant="secondary" className="text-xs">Coming Soon</Badge>}
                      </CardTitle>
                      <CardDescription>{method.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {method.needs && (
                        <p className="text-xs text-secondary">
                          Requires: {method.needs.replace('_', ' ')}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="profiles" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Server Selection */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Server className="w-4 h-4" />
                      Generation Server
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Select value={selectedServer} onValueChange={setSelectedServer}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select server" />
                      </SelectTrigger>
                      <SelectContent>
                        {comfyUIServers.map((server) => (
                          <SelectItem key={server.id} value={server.id}>
                            {server.name} ({server.server_type})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </CardContent>
                </Card>

                {/* Profile Generation Settings */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="w-4 h-4" />
                      Profile Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Profile Type</Label>
                      <Select 
                        value={profileSettings.profile_type} 
                        onValueChange={(value) => setProfileSettings(prev => ({ ...prev, profile_type: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {profileTypes.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Pose Style</Label>
                      <Select 
                        value={profileSettings.pose_style} 
                        onValueChange={(value) => setProfileSettings(prev => ({ ...prev, pose_style: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {poseStyles.map((style) => (
                            <SelectItem key={style.value} value={style.value}>
                              {style.icon} {style.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>ControlNet Type</Label>
                      <Select 
                        value={profileSettings.controlnet_type} 
                        onValueChange={(value) => setProfileSettings(prev => ({ ...prev, controlnet_type: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {controlnetTypes.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Number of Images: {profileSettings.count}</Label>
                      <input
                        type="range"
                        min="2"
                        max="8"
                        value={profileSettings.count}
                        onChange={(e) => setProfileSettings(prev => ({ ...prev, count: parseInt(e.target.value) }))}
                        className="w-full"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={createCharacter} disabled={loading || !characterData.name.trim()}>
              <Users className="w-4 h-4 mr-2" />
              {loading ? 'Creating...' : 'Create Character'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Generated Profiles Dialog */}
      <Dialog open={showProfiles} onOpenChange={setShowProfiles}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Generated Character Profiles
            </DialogTitle>
            <DialogDescription>
              Professional character variations using {profileSettings.controlnet_type}
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {generatedProfiles.map((profile, index) => (
              <Card key={index}>
                <CardHeader className="pb-2">
                  <Badge variant="outline" className="w-fit">
                    {profile.description}
                  </Badge>
                </CardHeader>
                <CardContent>
                  <div className="aspect-square rounded-lg overflow-hidden border mb-2">
                    <img
                      src={profile.url}
                      alt={profile.description}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => window.open(profile.url, '_blank')}
                  >
                    <Download className="w-3 h-3 mr-1" />
                    Download
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <DialogFooter>
            <Button onClick={() => setShowProfiles(false)}>
              Done
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AdvancedCharacterCreator;
