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
  
  // Model presets support
  const [modelPresets, setModelPresets] = useState({});
  const [selectedPreset, setSelectedPreset] = useState('fast');
  const [availableParameters, setAvailableParameters] = useState({});
  
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
    scheduler: 'normal',
    // Video-specific parameters
    video_fps: 24,
    video_frames: 14,
    motion_bucket_id: 127
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
      
      // Load gallery
      fetchGallery();
    }
  }, [clip, open]);

  useEffect(() => {
    if (selectedServer) {
      fetchServerInfo(selectedServer);
    }
  }, [selectedServer]);

  useEffect(() => {
    if (selectedModel) {
      fetchModelPresets(selectedModel);
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

  const fetchModelPresets = async (modelName) => {
    try {
      const response = await axios.get(`${API}/models/presets/${encodeURIComponent(modelName)}`);
      setModelPresets(response.data.presets || {});
      
      // Auto-apply fast preset by default
      if (response.data.presets?.fast) {
        applyPreset('fast', response.data.presets.fast);
      }
      
      // Fetch available parameters for this model
      fetchAvailableParameters(modelName);
    } catch (error) {
      console.error('Error fetching model presets:', error);
      toast.error('Failed to fetch model presets');
    }
  };

  const fetchAvailableParameters = async (modelName) => {
    try {
      const response = await axios.get(`${API}/models/parameters/${encodeURIComponent(modelName)}`);
      setAvailableParameters(response.data.parameters || {});
    } catch (error) {
      console.error('Error fetching model parameters:', error);
    }
  };

  const applyPreset = (presetName, presetConfig) => {
    setSelectedPreset(presetName);
    setGenerationParams(prev => ({
      ...prev,
      steps: presetConfig.steps || prev.steps,
      cfg: presetConfig.cfg || prev.cfg,
      width: presetConfig.width || prev.width,
      height: presetConfig.height || prev.height,
      sampler: presetConfig.sampler || prev.sampler,
      scheduler: presetConfig.scheduler || prev.scheduler,
      video_fps: presetConfig.video_fps || prev.video_fps,
      video_frames: presetConfig.video_frames || prev.video_frames
    }));
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
    if (!selectedServer || !selectedModel) {
      toast.error('Please select a server and model');
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
        model: selectedModel,
        loras: lorasData, // Multiple LoRAs
        generation_type: activeTab,
        params: {
          ...generationParams,
          ...advancedParams,
          seed: generationParams.seed === -1 ? Math.floor(Math.random() * 1000000) : generationParams.seed
        }
      };

      await axios.post(`${API}/generate`, requestData);
      
      toast.success(`${activeTab === 'image' ? 'Image' : 'Video'} generation started successfully`);
      
      // Update clip prompts
      await updateClipPrompts();
      
      // Refresh gallery
      setTimeout(() => {
        fetchGallery();
      }, 2000);
      
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

  const renderGallery = (contentList, contentType) => {
    if (!contentList || contentList.length === 0) {
      return (
        <div className="text-center py-8 text-secondary">
          No {contentType}s generated yet
        </div>
      );
    }

    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {contentList.map((content, index) => (
          <Card 
            key={content.id} 
            className={`cursor-pointer transition-all ${
              content.is_selected 
                ? 'ring-2 ring-indigo-500 bg-indigo-500/10' 
                : 'hover:ring-1 hover:ring-gray-500'
            }`}
            onClick={() => selectContent(content.id, contentType)}
            data-testid={`gallery-${contentType}-${index}`}
          >
            <CardContent className="p-3">
              <div 
                className="aspect-square bg-panel-dark rounded mb-2 flex items-center justify-center cursor-pointer relative group"
                onClick={() => handleContentClick(content)}
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
                {content.is_selected && (
                  <Badge variant="default" className="bg-indigo-600 text-xs">
                    Selected
                  </Badge>
                )}
                <div className="text-xs text-secondary truncate">
                  {content.prompt.substring(0, 50)}...
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
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2 bg-panel-dark mb-4">
                  <TabsTrigger value="image" className="data-[state=active]:bg-indigo-600">
                    <Image className="w-4 h-4 mr-2" />
                    Images ({gallery.images?.length || 0})
                  </TabsTrigger>
                  <TabsTrigger value="video" className="data-[state=active]:bg-indigo-600">
                    <Video className="w-4 h-4 mr-2" />
                    Videos ({gallery.videos?.length || 0})
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="image">
                  {renderGallery(gallery.images, 'image')}
                </TabsContent>
                
                <TabsContent value="video">
                  {renderGallery(gallery.videos, 'video')}
                </TabsContent>
              </Tabs>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-6">
              {/* Generation Type Tabs */}
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2 bg-panel-dark">
                  <TabsTrigger value="image" className="data-[state=active]:bg-indigo-600">
                    <Image className="w-4 h-4 mr-2" />
                    Image Generation
                  </TabsTrigger>
                  <TabsTrigger value="video" className="data-[state=active]:bg-indigo-600">
                    <Video className="w-4 h-4 mr-2" />
                    Video Generation
                  </TabsTrigger>
                </TabsList>
              </Tabs>

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
                        {activeTab === 'image' ? 'Image' : 'Video'} Prompt
                      </Label>
                      <Textarea
                        className="form-input min-h-[80px]"
                        placeholder={`Describe the ${activeTab} you want to generate...`}
                        value={prompts[activeTab]}
                        onChange={(e) => setPrompts(prev => ({
                          ...prev,
                          [activeTab]: e.target.value
                        }))}
                        data-testid={`${activeTab}-prompt-input`}
                      />
                    </div>
                    
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
                  </div>

                  {/* Model Selection */}
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

                    {/* Model Presets */}
                    {Object.keys(modelPresets).length > 0 && (
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-primary">Quality Preset</Label>
                        <div className="flex space-x-2">
                          {Object.entries(modelPresets).map(([presetName, presetConfig]) => (
                            <Button
                              key={presetName}
                              type="button"
                              variant={selectedPreset === presetName ? "default" : "outline"}
                              size="sm"
                              onClick={() => applyPreset(presetName, presetConfig)}
                              className={selectedPreset === presetName ? "btn-primary" : "btn-secondary"}
                              data-testid={`preset-${presetName}`}
                            >
                              <Zap className="w-3 h-3 mr-1" />
                              {presetName === 'fast' ? 'Fast' : 'Quality'}
                            </Button>
                          ))}
                        </div>
                        {availableParameters && (
                          <div className="text-xs text-muted-foreground">
                            {availableParameters.specializes_in && (
                              <span>Specializes in: {availableParameters.specializes_in.replace('_', ' ')}</span>
                            )}
                            {availableParameters.supports_lora !== undefined && (
                              <span className="ml-2">LoRA: {availableParameters.supports_lora ? '✓' : '✗'}</span>
                            )}
                            {availableParameters.max_loras && availableParameters.max_loras > 0 && (
                              <span className="ml-2">Max LoRAs: {availableParameters.max_loras}</span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    
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

                  {/* Generation Parameters */}
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

                        {/* Video Parameters - only show for video tab */}
                        {activeTab === 'video' && (
                          <div className="space-y-4 border-t border-panel pt-4">
                            <Label className="text-sm font-medium text-primary">Video Settings</Label>
                            <div className="grid grid-cols-2 gap-4">
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">FPS</Label>
                                <Select 
                                  value={generationParams.video_fps?.toString()} 
                                  onValueChange={(value) => updateParam('video_fps', parseInt(value))}
                                >
                                  <SelectTrigger className="form-input text-sm" data-testid="fps-select">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent className="bg-panel border-panel">
                                    {[6, 8, 12, 16, 24, 30].map(fps => (
                                      <SelectItem key={fps} value={fps.toString()} className="text-primary">
                                        {fps} FPS
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="space-y-2">
                                <Label className="text-xs text-secondary">Frames</Label>
                                <Select 
                                  value={generationParams.video_frames?.toString()} 
                                  onValueChange={(value) => updateParam('video_frames', parseInt(value))}
                                >
                                  <SelectTrigger className="form-input text-sm" data-testid="frames-select">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent className="bg-panel border-panel">
                                    {[8, 14, 16, 20, 24, 25, 30].map(frames => (
                                      <SelectItem key={frames} value={frames.toString()} className="text-primary">
                                        {frames} frames
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            </div>
                            <div className="space-y-2">
                              <Label className="text-xs text-secondary">Motion Bucket ID (SVD only)</Label>
                              <Input
                                type="number"
                                min="1"
                                max="255"
                                className="form-input text-sm"
                                value={generationParams.motion_bucket_id}
                                onChange={(e) => updateParam('motion_bucket_id', parseInt(e.target.value))}
                                data-testid="motion-bucket-input"
                              />
                            </div>
                          </div>
                        )}
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
                disabled={isGenerating || !selectedServer || !prompts[activeTab].trim() || !serverInfo?.is_online}
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
                    Generate {activeTab}
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