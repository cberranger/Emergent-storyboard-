import React, { useState, useEffect } from 'react';
import { Wand2, Image, Video, Server, Settings, Cpu, Zap, Eye, Grid, X, Plus, Minus } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { toast } from 'sonner';
import axios from 'axios';
import MediaViewerDialog from './MediaViewerDialog';

// Auto-detect environment  
const isDevelopment = process.env.NODE_ENV === 'development';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 
  (isDevelopment ? 'http://localhost:8001' : window.location.origin);
const API = `${BACKEND_URL}/api`;

const EnhancedGenerationDialog = ({ open, onOpenChange, clip, servers, onGenerated }) => {
  const [activeTab, setActiveTab] = useState('image');
  const [selectedServer, setSelectedServer] = useState('');
  const [serverInfo, setServerInfo] = useState(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedLora, setSelectedLora] = useState('none');
  const [modelDefaults, setModelDefaults] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [gallery, setGallery] = useState({ images: [], videos: [] });
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const [availableWorkflows, setAvailableWorkflows] = useState([]);
  const [isUploadingFace, setIsUploadingFace] = useState(false);
  const [showArchive, setShowArchive] = useState(false);
  const [archivedContent, setArchivedContent] = useState({ images: [], videos: [] });
  
  // Multiple LoRAs support
  const [loras, setLoras] = useState([{ name: 'none', weight: 1.0 }]);
  
  const [prompts, setPrompts] = useState({
    image: '',
    video: '',
    imageNegative: '',
    videoNegative: ''
  });
  
  const [generationParams, setGenerationParams] = useState({
    steps: 20,
    cfg: 7.0,
    width: 1024,
    height: 1024,
    seed: -1,
    sampler: 'euler',
    scheduler: 'normal'
  });

  // Advanced parameters
  const [advancedParams, setAdvancedParams] = useState({
    // Refiner
    use_refiner: false,
    refiner_model: '',
    refiner_switch: 0.8,
    
    // Face processing
    use_reactor: false,
    reactor_face_image: '',
    use_faceswap: false,
    
    // Upscaling
    use_upscale: false,
    upscale_factor: 2.0,
    upscale_model: 'RealESRGAN_x2plus',
    
    // Advanced settings
    pag_scale: 0.0, // Perturbed-Attention Guidance Scale
    clip_skip: 1,
    
    // ComfyUI workflow
    use_custom_workflow: false,
    workflow_json: ''
  });

  // InfiniteTalk parameters
  const [infiniteTalkParams, setInfiniteTalkParams] = useState({
    enabled: false,
    input_type: 'image', // 'image' or 'video'
    person_count: 'single', // 'single' or 'multi'
    source_image_id: '',
    audio_start_time: 0,
    audio_end_time: null,
    quality_mode: 'high', // 'fast' or 'high'
    width: 512,
    height: 512
  });

  // Available samplers and schedulers
  const samplers = [
    'euler', 'euler_a', 'heun', 'heunpp2', 'dpm_2', 'dpm_2_a', 'lms', 'dpm_fast',
    'dpm_adaptive', 'dpmpp_2s_a', 'dpmpp_sde', 'dpmpp_2m', 'dpmpp_2m_sde', 
    'ddim', 'uni_pc', 'uni_pc_bh2'
  ];

  const schedulers = [
    'normal', 'karras', 'exponential', 'sgm_uniform', 'simple', 'ddim_uniform'
  ];

  useEffect(() => {
    if (clip && open) {
      // Load clip prompts
      setPrompts({
        image: clip.image_prompt || '',
        video: clip.video_prompt || '',
        imageNegative: '',
        videoNegative: ''
      });
      
      // Load gallery and archive
      fetchGallery();
      fetchArchive();
    }
  }, [clip, open]);

  useEffect(() => {
    if (selectedServer) {
      fetchServerInfo(selectedServer);
    }
  }, [selectedServer]);

  useEffect(() => {
    if (selectedModel) {
      fetchModelDefaults(selectedModel);
    }
  }, [selectedModel]);

  const fetchServerInfo = async (serverId) => {
    try {
      const response = await axios.get(`${API}/comfyui/servers/${serverId}/info`);
      setServerInfo(response.data);
      
      // Auto-select first model if available
      if (response.data.models.length > 0) {
        setSelectedModel(response.data.models[0].name);
      }
      
      // Fetch available workflows
      fetchServerWorkflows(serverId);
    } catch (error) {
      console.error('Error fetching server info:', error);
      toast.error('Failed to fetch server info');
    }
  };

  const fetchServerWorkflows = async (serverId) => {
    try {
      const response = await axios.get(`${API}/comfyui/servers/${serverId}/workflows`);
      setAvailableWorkflows(response.data.workflows || []);
    } catch (error) {
      console.error('Error fetching workflows:', error);
      setAvailableWorkflows([]);
    }
  };

  const fetchModelDefaults = async (modelName) => {
    try {
      const response = await axios.get(`${API}/models/defaults/${encodeURIComponent(modelName)}`);
      setModelDefaults(response.data);
      setGenerationParams(prev => ({
        ...prev,
        ...response.data.defaults
      }));
    } catch (error) {
      console.error('Error fetching model defaults:', error);
    }
  };

  const fetchGallery = async () => {
    if (!clip?.id) return;
    
    try {
      const response = await axios.get(`${API}/clips/${clip.id}/gallery`);
      setGallery(response.data);
    } catch (error) {
      console.error('Error fetching gallery:', error);
    }
  };

  const handleGenerate = async () => {
    const isInfiniteTalk = infiniteTalkParams.enabled;
    
    if (!selectedServer) {
      toast.error('Please select a server');
      return;
    }

    if (!isInfiniteTalk && !selectedModel) {
      toast.error('Please select a model');
      return;
    }

    if (!serverInfo?.is_online) {
      toast.error('Selected server is offline');
      return;
    }

    const prompt = prompts[activeTab];
    const negativePrompt = prompts[`${activeTab}Negative`];

    if (!prompt.trim()) {
      toast.error(`Please enter a ${activeTab} prompt`);
      return;
    }

    // InfiniteTalk validation
    if (isInfiniteTalk) {
      if (!infiniteTalkParams.source_image_id) {
        toast.error('Please select an image from the gallery for InfiniteTalk');
        return;
      }
      
      // Check if selected server is RunPod
      const server = servers.find(s => s.id === selectedServer);
      if (!server?.url?.includes('runpod.ai') && server?.server_type !== 'runpod') {
        toast.error('InfiniteTalk is only available on RunPod serverless endpoints');
        return;
      }
    }

    setIsGenerating(true);
    
    try {
      // Prepare LoRAs data
      const lorasData = loras
        .filter(lora => lora.name !== 'none')
        .map(lora => ({ name: lora.name, weight: lora.weight }));

      const requestData = {
        clip_id: clip.id,
        server_id: selectedServer,
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim(),
        model: isInfiniteTalk ? 'InfiniteTalk' : selectedModel,
        loras: isInfiniteTalk ? [] : lorasData, // LoRAs not used for InfiniteTalk
        generation_type: isInfiniteTalk ? 'infinitetalk' : activeTab,
        params: isInfiniteTalk ? infiniteTalkParams : {
          ...generationParams,
          ...advancedParams,
          seed: generationParams.seed === -1 ? Math.floor(Math.random() * 1000000) : generationParams.seed
        },
        infinitetalk_params: isInfiniteTalk ? infiniteTalkParams : null
      };

      await axios.post(`${API}/generate`, requestData);
      
      const generationType = isInfiniteTalk ? 'InfiniteTalk video' : (activeTab === 'image' ? 'Image' : 'Video');
      toast.success(`${generationType} generation started successfully`);
      
      // Update clip prompts
      await updateClipPrompts();
      
      // Refresh gallery
      setTimeout(() => {
        fetchGallery();
      }, isInfiniteTalk ? 5000 : 2000); // InfiniteTalk takes longer
      
      onGenerated();
    } catch (error) {
      console.error('Error generating content:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to generate content';
      toast.error(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const updateClipPrompts = async () => {
    try {
      await axios.put(`${API}/clips/${clip.id}/prompts`, null, {
        params: {
          image_prompt: prompts.image,
          video_prompt: prompts.video
        }
      });
    } catch (error) {
      console.error('Error updating prompts:', error);
    }
  };

  const selectContent = async (contentId, contentType) => {
    try {
      await axios.put(`${API}/clips/${clip.id}/select-content`, null, {
        params: {
          content_id: contentId,
          content_type: contentType
        }
      });
      
      toast.success(`Selected ${contentType}`);
      fetchGallery();
    } catch (error) {
      console.error('Error selecting content:', error);
      toast.error('Failed to select content');
    }
  };

  const updateParam = (key, value) => {
    setGenerationParams(prev => ({
      ...prev,
      [key]: parseFloat(value) || value
    }));
  };

  const updateAdvancedParam = (key, value) => {
    setAdvancedParams(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const updateInfiniteTalkParam = (key, value) => {
    setInfiniteTalkParams(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const addLora = () => {
    setLoras(prev => [...prev, { name: 'none', weight: 1.0 }]);
  };

  const removeLora = (index) => {
    if (loras.length > 1) {
      setLoras(prev => prev.filter((_, i) => i !== index));
    }
  };

  const updateLora = (index, field, value) => {
    setLoras(prev => prev.map((lora, i) => 
      i === index ? { ...lora, [field]: field === 'weight' ? parseFloat(value) || 0 : value } : lora
    ));
  };

  const handleContentClick = (content) => {
    setSelectedContent(content);
    setShowMediaViewer(true);
  };

  const fetchArchive = async () => {
    if (!clip?.scene_id) return;
    
    try {
      // Get project ID from scene
      const sceneResponse = await axios.get(`${API}/scenes/${clip.scene_id}`);
      const projectId = sceneResponse.data.project_id;
      
      const response = await axios.get(`${API}/projects/${projectId}/archive`);
      setArchivedContent(response.data);
    } catch (error) {
      console.error('Error fetching archive:', error);
    }
  };

  const discardContent = async (contentId, contentType) => {
    try {
      await axios.put(`${API}/clips/${clip.id}/discard-content`, null, {
        params: { content_id: contentId, content_type: contentType }
      });
      
      toast.success(`${contentType} moved to archive`);
      fetchGallery();
      fetchArchive();
    } catch (error) {
      console.error('Error discarding content:', error);
      toast.error('Failed to move to archive');
    }
  };

  const deleteContent = async (contentId, contentType) => {
    if (!confirm(`Are you sure you want to permanently delete this ${contentType}?`)) {
      return;
    }
    
    try {
      await axios.delete(`${API}/clips/${clip.id}/delete-content`, {
        params: { content_id: contentId, content_type: contentType }
      });
      
      toast.success(`${contentType} deleted permanently`);
      fetchGallery();
    } catch (error) {
      console.error('Error deleting content:', error);
      toast.error('Failed to delete content');
    }
  };

  const restoreContent = async (contentId, contentType) => {
    if (!clip?.scene_id) return;
    
    try {
      // Get project ID from scene
      const sceneResponse = await axios.get(`${API}/scenes/${clip.scene_id}`);
      const projectId = sceneResponse.data.project_id;
      
      await axios.put(`${API}/projects/${projectId}/restore-content`, null, {
        params: { 
          content_id: contentId, 
          content_type: contentType, 
          target_clip_id: clip.id 
        }
      });
      
      toast.success(`${contentType} restored to clip`);
      fetchGallery();
      fetchArchive();
    } catch (error) {
      console.error('Error restoring content:', error);
      toast.error('Failed to restore content');
    }
  };

  const handleFaceUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }

    setIsUploadingFace(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API}/upload-face-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      updateAdvancedParam('reactor_face_image', response.data.file_url);
      toast.success('Face image uploaded successfully');
    } catch (error) {
      console.error('Error uploading face image:', error);
      toast.error('Failed to upload face image');
    } finally {
      setIsUploadingFace(false);
    }
  };

  const renderGallery = (contentList, contentType, isArchive = false) => {
    if (!contentList || contentList.length === 0) {
      return (
        <div className="text-center py-8 text-secondary">
          No {contentType}s {isArchive ? 'in archive' : 'generated yet'}
        </div>
      );
    }

    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {contentList.map((content, index) => (
          <Card 
            key={content.id} 
            className={`cursor-pointer transition-all ${
              content.is_selected && !isArchive
                ? 'ring-2 ring-indigo-500 bg-indigo-500/10' 
                : 'hover:ring-1 hover:ring-gray-500'
            }`}
            onClick={(e) => {
              if (!isArchive) {
                selectContent(content.id, contentType);
              }
              e.stopPropagation();
            }}
            data-testid={`gallery-${contentType}-${index}`}
          >
            <CardContent className="p-3">
              <div 
                className="aspect-square bg-panel-dark rounded mb-2 flex items-center justify-center cursor-pointer relative group"
                onClick={(e) => {
                  handleContentClick(content);
                  e.stopPropagation();
                }}
              >
                {content.url ? (
                  <>
                    {contentType === 'image' ? (
                      <img 
                        src={content.url} 
                        alt="Generated" 
                        className="w-full h-full object-cover rounded"
                      />
                    ) : (
                      <video 
                        src={content.url} 
                        className="w-full h-full object-cover rounded"
                        controls={false}
                      />
                    )}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded flex items-center justify-center">
                      <Eye className="w-6 h-6 text-white" />
                    </div>
                  </>
                ) : (
                  <div className="text-secondary text-xs">Processing...</div>
                )}
              </div>
              
              <div className="space-y-1">
                <div className="text-xs text-secondary">
                  {content.model_name}
                </div>
                <div className="flex items-center gap-1 flex-wrap">
                  {content.is_selected && !isArchive && (
                    <Badge variant="default" className="bg-indigo-600 text-xs">
                      Selected
                    </Badge>
                  )}
                  {isArchive && (
                    <Badge variant="outline" className="bg-amber-600/20 text-amber-400 border-amber-500/30 text-xs">
                      Archived
                    </Badge>
                  )}
                </div>
                <div className="text-xs text-secondary truncate">
                  {content.prompt.substring(0, 50)}...
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-1 pt-1">
                  {!isArchive ? (
                    <>
                      {infiniteTalkParams.enabled && contentType === 'image' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            updateInfiniteTalkParam('source_image_id', content.id);
                            toast.success('Image selected for InfiniteTalk');
                          }}
                          className="text-xs p-1 h-6"
                        >
                          Use for InfiniteTalk
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          discardContent(content.id, contentType);
                        }}
                        className="text-xs p-1 h-6 text-amber-400 hover:text-amber-300"
                      >
                        Archive
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteContent(content.id, contentType);
                        }}
                        className="text-xs p-1 h-6 text-red-400 hover:text-red-300"
                      >
                        Delete
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        restoreContent(content.id, contentType);
                      }}
                      className="text-xs p-1 h-6 text-green-400 hover:text-green-300"
                    >
                      Restore
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  if (!clip) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-primary flex items-center">
              <Wand2 className="w-5 h-5 mr-2" />
              Generate Content for "{clip.name}"
            </DialogTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowGallery(!showGallery)}
              className="btn-secondary"
              data-testid="toggle-gallery-btn"
            >
              <Grid className="w-4 h-4 mr-2" />
              {showGallery ? 'Hide' : 'Show'} Gallery
            </Button>
          </div>
        </DialogHeader>

        <div className="flex flex-col h-full overflow-hidden">
          {showGallery ? (
            <div className="flex-1 overflow-y-auto">
              <Tabs value={showArchive ? 'archive' : activeTab} onValueChange={(value) => {
                if (value === 'archive') {
                  setShowArchive(true);
                } else {
                  setShowArchive(false);
                  setActiveTab(value);
                }
              }}>
                <TabsList className="grid w-full grid-cols-3 bg-panel-dark mb-4">
                  <TabsTrigger value="image" className="data-[state=active]:bg-indigo-600">
                    <Image className="w-4 h-4 mr-2" />
                    Images ({gallery.images?.filter(img => !img.is_archived)?.length || 0})
                  </TabsTrigger>
                  <TabsTrigger value="video" className="data-[state=active]:bg-indigo-600">
                    <Video className="w-4 h-4 mr-2" />
                    Videos ({gallery.videos?.filter(vid => !vid.is_archived)?.length || 0})
                  </TabsTrigger>
                  <TabsTrigger value="archive" className="data-[state=active]:bg-indigo-600">
                    <Grid className="w-4 h-4 mr-2" />
                    Archive ({(archivedContent.images?.length || 0) + (archivedContent.videos?.length || 0)})
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="image">
                  {renderGallery(gallery.images?.filter(img => !img.is_archived), 'image')}
                </TabsContent>
                
                <TabsContent value="video">
                  {renderGallery(gallery.videos?.filter(vid => !vid.is_archived), 'video')}
                </TabsContent>

                <TabsContent value="archive">
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-sm font-medium text-primary mb-3">Archived Images</h3>
                      {renderGallery(archivedContent.images, 'image', true)}
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-primary mb-3">Archived Videos</h3>
                      {renderGallery(archivedContent.videos, 'video', true)}
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-6">
              {/* Generation Type Tabs */}
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-3 bg-panel-dark">
                  <TabsTrigger value="image" className="data-[state=active]:bg-indigo-600">
                    <Image className="w-4 h-4 mr-2" />
                    Image Generation
                  </TabsTrigger>
                  <TabsTrigger value="video" className="data-[state=active]:bg-indigo-600">
                    <Video className="w-4 h-4 mr-2" />
                    Video Generation
                  </TabsTrigger>
                  <TabsTrigger value="infinitetalk" className="data-[state=active]:bg-indigo-600">
                    <Wand2 className="w-4 h-4 mr-2" />
                    InfiniteTalk
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              {/* InfiniteTalk Mode Indicator */}
              {activeTab === 'infinitetalk' && (
                <div className="flex items-center space-x-2 p-3 bg-green-900/20 rounded-lg border border-green-600/30">
                  <Wand2 className="w-4 h-4 text-green-400" />
                  <Label className="text-sm text-green-400">InfiniteTalk Mode Active - Generate lip-sync videos from images</Label>
                </div>
              )}

              {/* Server Selection */}
              <div className="space-y-3">
                <Label className="text-sm font-medium text-primary">ComfyUI Server</Label>
                {servers.length === 0 ? (
                  <div className="text-center py-8 bg-panel-dark rounded-lg border border-panel">
                    <Server className="w-8 h-8 text-secondary mx-auto mb-2" />
                    <p className="text-secondary text-sm">No servers configured</p>
                  </div>
                ) : (
                  <>
                    <Select value={selectedServer} onValueChange={setSelectedServer}>
                      <SelectTrigger className="form-input" data-testid="server-select">
                        <SelectValue placeholder="Select a ComfyUI server" />
                      </SelectTrigger>
                      <SelectContent className="bg-panel border-panel">
                        {servers.map((server) => (
                          <SelectItem key={server.id} value={server.id}>
                            <div className="flex items-center space-x-2">
                              <span>{server.name}</span>
                              <Badge variant="outline" className="text-xs">
                                {server.url}
                              </Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    
                    {serverInfo && (
                      <div className="flex items-center space-x-3">
                        <Badge 
                          variant={serverInfo.is_online ? 'default' : 'secondary'}
                          className={
                            serverInfo.is_online 
                              ? 'bg-green-500/20 text-green-400 border-green-500/30'
                              : 'bg-red-500/20 text-red-400 border-red-500/30'
                          }
                        >
                          {serverInfo.is_online ? 'Online' : 'Offline'}
                        </Badge>
                        <span className="text-xs text-secondary">
                          {serverInfo.models.length} models, {serverInfo.loras.length} LoRAs
                        </span>
                      </div>
                    )}
                  </>
                )}
              </div>

              {serverInfo?.is_online && (
                <>
                  {/* Prompts */}
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-primary">
                        {activeTab === 'infinitetalk' ? 'Description' : (activeTab === 'image' ? 'Image' : 'Video')} Prompt
                      </Label>
                      <Textarea
                        className="form-input min-h-[80px]"
                        placeholder={
                          activeTab === 'infinitetalk' 
                            ? "Describe the person or scene (e.g., 'A person talking naturally')" 
                            : `Describe the ${activeTab} you want to generate...`
                        }
                        value={prompts[activeTab === 'infinitetalk' ? 'video' : activeTab]}
                        onChange={(e) => setPrompts(prev => ({
                          ...prev,
                          [activeTab === 'infinitetalk' ? 'video' : activeTab]: e.target.value
                        }))}
                        data-testid={`${activeTab}-prompt-input`}
                      />
                    </div>
                    
                    {activeTab !== 'infinitetalk' && (
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-primary">Negative Prompt</Label>
                        <Textarea
                          className="form-input min-h-[60px]"
                          placeholder="Describe what you don't want..."
                          value={prompts[`${activeTab}Negative`]}
                          onChange={(e) => setPrompts(prev => ({
                            ...prev,
                            [`${activeTab}Negative`]: e.target.value
                          }))}
                          data-testid={`${activeTab}-negative-prompt-input`}
                        />
                      </div>
                    )}
                  </div>

                  {/* InfiniteTalk Parameters */}
                  {activeTab === 'infinitetalk' && (
                    <Card className="bg-panel-dark border-panel">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-primary">InfiniteTalk Settings</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {/* Source Image Selection */}
                        <div className="space-y-2">
                          <Label className="text-sm text-primary">Source Image</Label>
                          <Select 
                            value={infiniteTalkParams.source_image_id} 
                            onValueChange={(value) => updateInfiniteTalkParam('source_image_id', value)}
                          >
                            <SelectTrigger className="form-input">
                              <SelectValue placeholder="Select an image from gallery" />
                            </SelectTrigger>
                            <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                              {gallery.images?.filter(img => !img.is_archived)?.map((image, index) => (
                                <SelectItem key={image.id} value={image.id} className="text-primary">
                                  Image #{index + 1} - {image.prompt.substring(0, 30)}...
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          {!gallery.images?.length && (
                            <p className="text-xs text-secondary">Generate some images first to use with InfiniteTalk</p>
                          )}
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          {/* Input Type */}
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Input Type</Label>
                            <Select 
                              value={infiniteTalkParams.input_type} 
                              onValueChange={(value) => updateInfiniteTalkParam('input_type', value)}
                            >
                              <SelectTrigger className="form-input text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                <SelectItem value="image" className="text-primary">Image-to-Video</SelectItem>
                                <SelectItem value="video" className="text-primary">Video-to-Video</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          {/* Person Count */}
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Person Count</Label>
                            <Select 
                              value={infiniteTalkParams.person_count} 
                              onValueChange={(value) => updateInfiniteTalkParam('person_count', value)}
                            >
                              <SelectTrigger className="form-input text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                <SelectItem value="single" className="text-primary">Single Person</SelectItem>
                                <SelectItem value="multi" className="text-primary">Multiple People</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          {/* Quality Mode */}
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Quality Mode</Label>
                            <Select 
                              value={infiniteTalkParams.quality_mode} 
                              onValueChange={(value) => updateInfiniteTalkParam('quality_mode', value)}
                            >
                              <SelectTrigger className="form-input text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                <SelectItem value="fast" className="text-primary">
                                  Fast (Lower quality, faster generation)
                                </SelectItem>
                                <SelectItem value="high" className="text-primary">
                                  High Quality (Better results, slower)
                                </SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          {/* Resolution */}
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Resolution</Label>
                            <Select 
                              value={`${infiniteTalkParams.width}x${infiniteTalkParams.height}`} 
                              onValueChange={(value) => {
                                const [width, height] = value.split('x').map(Number);
                                updateInfiniteTalkParam('width', width);
                                updateInfiniteTalkParam('height', height);
                              }}
                            >
                              <SelectTrigger className="form-input text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                <SelectItem value="512x512" className="text-primary">512x512</SelectItem>
                                <SelectItem value="768x768" className="text-primary">768x768</SelectItem>
                                <SelectItem value="1024x1024" className="text-primary">1024x1024</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        {/* Audio Timing - Placeholder for future implementation */}
                        <div className="space-y-2">
                          <Label className="text-xs text-secondary">Audio Timing (Project Audio)</Label>
                          <div className="grid grid-cols-2 gap-2">
                            <Input
                              type="number"
                              min="0"
                              step="0.1"
                              placeholder="Start time (s)"
                              className="form-input text-sm"
                              value={infiniteTalkParams.audio_start_time}
                              onChange={(e) => updateInfiniteTalkParam('audio_start_time', parseFloat(e.target.value) || 0)}
                            />
                            <Input
                              type="number"
                              min="0"
                              step="0.1"
                              placeholder="End time (s)"
                              className="form-input text-sm"
                              value={infiniteTalkParams.audio_end_time || ''}
                              onChange={(e) => updateInfiniteTalkParam('audio_end_time', e.target.value ? parseFloat(e.target.value) : null)}
                            />
                          </div>
                          <p className="text-xs text-secondary">Leave end time empty to use full audio</p>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Model Selection - Hidden for InfiniteTalk */}
                  {activeTab !== 'infinitetalk' && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-primary flex items-center">
                          <Cpu className="w-4 h-4 mr-1" />
                          Model
                          {modelDefaults.detected_type && (
                            <Badge variant="outline" className="ml-2 text-xs">
                              {modelDefaults.detected_type}
                            </Badge>
                          )}
                        </Label>
                        <Select value={selectedModel} onValueChange={setSelectedModel}>
                          <SelectTrigger className="form-input" data-testid="model-select">
                            <SelectValue placeholder="Select model" />
                          </SelectTrigger>
                          <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                            {serverInfo.models.map((model, index) => (
                              <SelectItem 
                                key={index} 
                                value={model.name} 
                                className="text-primary hover:bg-panel-dark"
                              >
                                {model.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    
                      {/* Multiple LoRAs */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm font-medium text-primary">LoRAs</Label>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={addLora}
                            className="btn-secondary"
                            data-testid="add-lora-btn"
                          >
                            <Plus className="w-3 h-3 mr-1" />
                            Add LoRA
                          </Button>
                        </div>
                      <div className="space-y-2">
                        {loras.map((lora, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <Select 
                              value={lora.name} 
                              onValueChange={(value) => updateLora(index, 'name', value)}
                            >
                              <SelectTrigger className="form-input flex-1">
                                <SelectValue placeholder="Select LoRA" />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                                <SelectItem value="none" className="text-primary hover:bg-panel-dark">
                                  None
                                </SelectItem>
                                {serverInfo.loras.map((availableLora, loraIndex) => (
                                  <SelectItem 
                                    key={loraIndex} 
                                    value={availableLora.name} 
                                    className="text-primary hover:bg-panel-dark"
                                  >
                                    {availableLora.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            
                            <div className="flex items-center space-x-2 min-w-24">
                              <Label className="text-xs text-secondary">Weight:</Label>
                              <Input
                                type="number"
                                min="0"
                                max="2"
                                step="0.1"
                                className="form-input w-16 text-xs"
                                value={lora.weight}
                                onChange={(e) => updateLora(index, 'weight', e.target.value)}
                                disabled={lora.name === 'none'}
                              />
                            </div>
                            
                            {loras.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeLora(index)}
                                className="btn-secondary"
                              >
                                <Minus className="w-3 h-3" />
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                    </div>
                  )}

                  {/* Generation Parameters - Hidden for InfiniteTalk */}
                  {activeTab !== 'infinitetalk' && (
                    <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="basic-params" className="border-panel">
                      <AccordionTrigger className="text-primary hover:text-primary">
                        <div className="flex items-center">
                          <Settings className="w-4 h-4 mr-2" />
                          Basic Parameters
                          {modelDefaults.detected_type && (
                            <span className="ml-2 text-xs text-secondary">
                              (Optimized for {modelDefaults.detected_type})
                            </span>
                          )}
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Steps</Label>
                            <Input
                              type="number"
                              min="1"
                              max="150"
                              className="form-input text-sm"
                              value={generationParams.steps}
                              onChange={(e) => updateParam('steps', e.target.value)}
                              data-testid="steps-input"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">CFG Scale</Label>
                            <Input
                              type="number"
                              min="1"
                              max="30"
                              step="0.1"
                              className="form-input text-sm"
                              value={generationParams.cfg}
                              onChange={(e) => updateParam('cfg', e.target.value)}
                              data-testid="cfg-input"
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Sampler</Label>
                            <Select 
                              value={generationParams.sampler} 
                              onValueChange={(value) => updateParam('sampler', value)}
                            >
                              <SelectTrigger className="form-input text-sm" data-testid="sampler-select">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                                {samplers.map(sampler => (
                                  <SelectItem key={sampler} value={sampler} className="text-primary">
                                    {sampler}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Scheduler</Label>
                            <Select 
                              value={generationParams.scheduler} 
                              onValueChange={(value) => updateParam('scheduler', value)}
                            >
                              <SelectTrigger className="form-input text-sm" data-testid="scheduler-select">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                {schedulers.map(scheduler => (
                                  <SelectItem key={scheduler} value={scheduler} className="text-primary">
                                    {scheduler}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Width</Label>
                            <Select 
                              value={generationParams.width.toString()} 
                              onValueChange={(value) => updateParam('width', value)}
                            >
                              <SelectTrigger className="form-input text-sm" data-testid="width-select">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                {[512, 768, 1024, 1280, 1536].map(size => (
                                  <SelectItem key={size} value={size.toString()} className="text-primary">
                                    {size}px
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Height</Label>
                            <Select 
                              value={generationParams.height.toString()} 
                              onValueChange={(value) => updateParam('height', value)}
                            >
                              <SelectTrigger className="form-input text-sm" data-testid="height-select">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-panel border-panel">
                                {[512, 768, 1024, 1280, 1536].map(size => (
                                  <SelectItem key={size} value={size.toString()} className="text-primary">
                                    {size}px
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">Seed (-1 for random)</Label>
                            <Input
                              type="number"
                              min="-1"
                              className="form-input text-sm"
                              value={generationParams.seed}
                              onChange={(e) => updateParam('seed', e.target.value)}
                              data-testid="seed-input"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label className="text-xs text-secondary">CLIP Skip</Label>
                            <Input
                              type="number"
                              min="1"
                              max="12"
                              className="form-input text-sm"
                              value={advancedParams.clip_skip}
                              onChange={(e) => updateAdvancedParam('clip_skip', parseInt(e.target.value))}
                              data-testid="clip-skip-input"
                            />
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>

                    <AccordionItem value="advanced-params" className="border-panel">
                      <AccordionTrigger className="text-primary hover:text-primary">
                        <div className="flex items-center">
                          <Zap className="w-4 h-4 mr-2" />
                          Advanced Parameters
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="space-y-4">
                        {/* PAG Scale */}
                        <div className="space-y-2">
                          <Label className="text-xs text-secondary">
                            Perturbed-Attention Guidance Scale (0 = disabled)
                          </Label>
                          <Input
                            type="number"
                            min="0"
                            max="10"
                            step="0.1"
                            className="form-input text-sm"
                            value={advancedParams.pag_scale}
                            onChange={(e) => updateAdvancedParam('pag_scale', parseFloat(e.target.value) || 0)}
                            data-testid="pag-scale-input"
                          />
                        </div>

                        {/* Refiner */}
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={advancedParams.use_refiner}
                              onCheckedChange={(checked) => updateAdvancedParam('use_refiner', checked)}
                            />
                            <Label className="text-sm text-primary">Use Refiner</Label>
                          </div>
                          {advancedParams.use_refiner && (
                            <div className="grid grid-cols-2 gap-4 pl-6">
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Refiner Model</Label>
                                <Select 
                                  value={advancedParams.refiner_model} 
                                  onValueChange={(value) => updateAdvancedParam('refiner_model', value)}
                                >
                                  <SelectTrigger className="form-input text-sm" data-testid="refiner-model-select">
                                    <SelectValue placeholder="Select refiner model" />
                                  </SelectTrigger>
                                  <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                                    {serverInfo?.models?.map((model, index) => (
                                      <SelectItem 
                                        key={index} 
                                        value={model.name} 
                                        className="text-primary hover:bg-panel-dark"
                                      >
                                        {model.name}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Refiner Switch (0-1)</Label>
                                <Input
                                  type="number"
                                  min="0"
                                  max="1"
                                  step="0.1"
                                  className="form-input text-sm"
                                  value={advancedParams.refiner_switch}
                                  onChange={(e) => updateAdvancedParam('refiner_switch', parseFloat(e.target.value))}
                                  data-testid="refiner-switch-input"
                                />
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Face Processing */}
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={advancedParams.use_reactor}
                              onCheckedChange={(checked) => updateAdvancedParam('use_reactor', checked)}
                              data-testid="reactor-switch"
                            />
                            <Label className="text-sm text-primary">Use Reactor (Face Swap)</Label>
                          </div>
                          {advancedParams.use_reactor && (
                            <div className="pl-6 space-y-3">
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Reference Face Image</Label>
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFaceUpload}
                                    className="hidden"
                                    id="face-upload"
                                    data-testid="face-upload-input"
                                  />
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => document.getElementById('face-upload')?.click()}
                                    disabled={isUploadingFace}
                                    className="btn-secondary"
                                    data-testid="face-upload-btn"
                                  >
                                    {isUploadingFace ? 'Uploading...' : 'Upload Face'}
                                  </Button>
                                  {advancedParams.reactor_face_image && (
                                    <span className="text-xs text-green-400">✓ Image uploaded</span>
                                  )}
                                </div>
                              </div>
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Or enter image URL</Label>
                                <Input
                                  className="form-input text-sm"
                                  placeholder="https://example.com/face.jpg"
                                  value={advancedParams.reactor_face_image}
                                  onChange={(e) => updateAdvancedParam('reactor_face_image', e.target.value)}
                                  data-testid="reactor-face-url-input"
                                />
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Upscaling */}
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={advancedParams.use_upscale}
                              onCheckedChange={(checked) => updateAdvancedParam('use_upscale', checked)}
                            />
                            <Label className="text-sm text-primary">Use Upscaling</Label>
                          </div>
                          {advancedParams.use_upscale && (
                            <div className="grid grid-cols-2 gap-4 pl-6">
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Upscale Factor</Label>
                                <Select 
                                  value={advancedParams.upscale_factor.toString()} 
                                  onValueChange={(value) => updateAdvancedParam('upscale_factor', parseFloat(value))}
                                >
                                  <SelectTrigger className="form-input text-sm">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent className="bg-panel border-panel">
                                    {[1.5, 2, 3, 4].map(factor => (
                                      <SelectItem key={factor} value={factor.toString()} className="text-primary">
                                        {factor}x
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Upscale Model</Label>
                                <Select 
                                  value={advancedParams.upscale_model} 
                                  onValueChange={(value) => updateAdvancedParam('upscale_model', value)}
                                >
                                  <SelectTrigger className="form-input text-sm">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent className="bg-panel border-panel">
                                    {['RealESRGAN_x2plus', 'RealESRGAN_x4plus', 'ESRGAN_4x', 'SwinIR_4x'].map(model => (
                                      <SelectItem key={model} value={model} className="text-primary">
                                        {model}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Custom Workflow */}
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={advancedParams.use_custom_workflow}
                              onCheckedChange={(checked) => updateAdvancedParam('use_custom_workflow', checked)}
                            />
                            <Label className="text-sm text-primary">Use Custom ComfyUI Workflow</Label>
                          </div>
                          {advancedParams.use_custom_workflow && (
                            <div className="pl-6 space-y-2">
                              <Label className="text-xs text-secondary">Workflow JSON</Label>
                              <Textarea
                                className="form-input text-sm min-h-[100px] font-mono"
                                placeholder='{"nodes": [...], "connections": [...]}'
                                value={advancedParams.workflow_json}
                                onChange={(e) => updateAdvancedParam('workflow_json', e.target.value)}
                              />
                            </div>
                          )}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                  )}
                </>
              )}
            </div>
          )}

          {/* Action Buttons */}
          {!showGallery && (
            <div className="flex justify-end space-x-3 pt-4 border-t border-panel">
              <Button 
                variant="outline" 
                onClick={() => onOpenChange(false)}
                className="btn-secondary"
                data-testid="cancel-generation-btn"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleGenerate}
                disabled={
                  isGenerating || 
                  !selectedServer || 
                  !prompts[activeTab === 'infinitetalk' ? 'video' : activeTab].trim() || 
                  !serverInfo?.is_online ||
                  (activeTab !== 'infinitetalk' && !selectedModel) ||
                  (activeTab === 'infinitetalk' && !infiniteTalkParams.source_image_id)
                }
                className="btn-primary"
                data-testid="start-generation-btn"
              >
                {isGenerating ? (
                  <>
                    <Zap className="w-4 h-4 mr-2 animate-pulse" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4 mr-2" />
                    Generate {activeTab === 'infinitetalk' ? 'InfiniteTalk Video' : activeTab}
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Media Viewer Dialog */}
        <MediaViewerDialog
          open={showMediaViewer}
          onOpenChange={setShowMediaViewer}
          content={selectedContent}
        />
      </DialogContent>
    </Dialog>
  );
};

export default EnhancedGenerationDialog;