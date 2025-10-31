import React, { useState, useEffect } from 'react';
import { Wand2, Image, Video, Server, Settings, Cpu, Zap, Eye, Grid, X, Plus, Minus, Database } from 'lucide-react';
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
import { comfyuiService, modelService, clipService, sceneService, characterService, generationService, poolService } from '@/services';
import { useNotifications } from '@/contexts/NotificationContext';
import MediaViewerDialog from './MediaViewerDialog';
import ResultsPreviewPanel from './ResultsPreviewPanel';
import {
  isValidUUID,
  validatePromptLength,
  validateGenerationParams,
  sanitizeInput
} from '@/utils/validators';
import {
  saveGenerationSettings,
  loadGenerationSettings,
  getModelSettings,
  saveModelSettings,
  applyModelSettings
} from '@/utils/generationSettings';

const EnhancedGenerationDialog = ({ open, onOpenChange, clip, servers, onGenerated }) => {
  const { addTrackedJob } = useNotifications();
  
  // Load persistent settings on component mount
  const savedSettings = loadGenerationSettings();
  
  const [activeTab, setActiveTab] = useState(savedSettings.activeTab);
  const [selectedServer, setSelectedServer] = useState(savedSettings.selectedServer);
  const [serverInfo, setServerInfo] = useState(null);
  const [selectedModels, setSelectedModels] = useState(savedSettings.selectedModels || []); // For multiple model selection
  const [useMultipleModels, setUseMultipleModels] = useState(savedSettings.useMultipleModels || false);
  const [selectedModel, setSelectedModel] = useState(savedSettings.selectedModel);
  const [modelDefaults, setModelDefaults] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [gallery, setGallery] = useState({ images: [], videos: [] });
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const [availableWorkflows, setAvailableWorkflows] = useState([]);
  const [isUploadingFace, setIsUploadingFace] = useState(false);

  // Model filtering and search
  const [modelSearchQuery, setModelSearchQuery] = useState('');
  const [filteredModels, setFilteredModels] = useState([]);
  
  // LoRA filtering and search
  const [loraSearchQueries, setLoraSearchQueries] = useState([]); // Array of queries for each LoRA slot

  // Model presets support
  const [modelPresets, setModelPresets] = useState({});
  const [selectedPreset, setSelectedPreset] = useState(savedSettings.selectedPreset || 'fast');
  const [availableParameters, setAvailableParameters] = useState({});

  // Multiple LoRAs support
  const [loras, setLoras] = useState(savedSettings.loras || [{ name: 'none', weight: 1.0 }]);
  const [provider, setProvider] = useState(savedSettings.provider || 'comfyui');
  const [soraReferenceImageUrl, setSoraReferenceImageUrl] = useState("");
  
  const [prompts, setPrompts] = useState({
    image: '',
    video: '',
    imageNegative: '',
    videoNegative: ''
  });
  
  const [generationParams, setGenerationParams] = useState(savedSettings.generationParams);
  
  // Advanced parameters
  const [advancedParams, setAdvancedParams] = useState(savedSettings.advancedParams);

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

  // Save settings whenever they change
  useEffect(() => {
    const currentSettings = {
      activeTab,
      selectedServer,
      selectedModel,
      selectedModels,
      useMultipleModels,
      selectedPreset,
      provider,
      generationParams,
      advancedParams,
      loras
    };
    saveGenerationSettings(currentSettings);
  }, [
    activeTab,
    selectedServer,
    selectedModel,
    selectedModels,
    useMultipleModels,
    selectedPreset,
    provider,
    generationParams,
    advancedParams,
    loras
  ]);
  
  // Apply model-specific settings when model changes
  useEffect(() => {
    if (selectedModel && provider === 'comfyui') {
      const modelSettings = getModelSettings(selectedModel);
      if (modelSettings) {
        // Apply saved model-specific settings
        if (modelSettings.generationParams) {
          setGenerationParams(prev => ({ ...prev, ...modelSettings.generationParams }));
        }
        if (modelSettings.advancedParams) {
          setAdvancedParams(prev => ({ ...prev, ...modelSettings.advancedParams }));
        }
        if (modelSettings.loras) {
          setLoras(modelSettings.loras);
        }
        if (modelSettings.selectedPreset) {
          setSelectedPreset(modelSettings.selectedPreset);
        }
      }
      fetchModelPresets(selectedModel);
    }
  }, [selectedModel]);
  
  // Save model-specific settings when they change
  useEffect(() => {
    if (selectedModel && provider === 'comfyui') {
      const modelSettings = {
        generationParams,
        advancedParams,
        loras,
        selectedPreset
      };
      saveModelSettings(selectedModel, modelSettings);
    }
  }, [generationParams, advancedParams, loras, selectedPreset, selectedModel, provider]);

  useEffect(() => {
    if (provider === 'openai') {
      setActiveTab('video');
      setSelectedModel(prev => (prev && prev.startsWith('sora-') ? prev : 'sora-2'));
    }
  }, [provider]);

  // Filter and sort models when serverInfo or search query changes
  useEffect(() => {
    if (serverInfo?.models) {
      let filtered = [...serverInfo.models];

      // Sort alphabetically by name
      filtered.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));

      // Apply search filter
      if (modelSearchQuery.trim()) {
        const query = modelSearchQuery.toLowerCase();
        filtered = filtered.filter(model =>
          model.name.toLowerCase().includes(query)
        );
      }

      setFilteredModels(filtered);
    } else {
      setFilteredModels([]);
    }
  }, [serverInfo, modelSearchQuery]);
  
  // Filter LoRAs based on search queries
  const getFilteredLoras = (loraIndex) => {
    if (!serverInfo?.loras || !Array.isArray(serverInfo.loras)) {
      return [];
    }
    
    let loras = [...serverInfo.loras];
    // Sort alphabetically by name
    loras.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
    
    // Apply search filter if exists for this specific LoRA slot
    const searchQuery = loraSearchQueries[loraIndex] || '';
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      loras = loras.filter(lora =>
        lora.name.toLowerCase().includes(query)
      );
    }
    
    return loras;
  };

  // Helper function to get online servers only
  const getOnlineServers = () => {
    return servers.filter(server => {
      // Check if we have server info cached, or assume online if not checked yet
      return server.is_active !== false; // Will be refined once we fetch server info
    });
  };

  const fetchServerInfo = async (serverId) => {
    try {
      const data = await comfyuiService.getServerInfo(serverId);
      setServerInfo(data);
      
      if (data.models.length > 0) {
        setSelectedModel(data.models[0].name);
      }
      
      fetchServerWorkflows(serverId);
    } catch (error) {
      console.error('Error fetching server info:', error);
    }
  };

  const fetchServerWorkflows = async (serverId) => {
    try {
      const data = await comfyuiService.getServerWorkflows(serverId);
      setAvailableWorkflows(data.workflows || []);
    } catch (error) {
      console.error('Error fetching workflows:', error);
      setAvailableWorkflows([]);
    }
  };

  const fetchModelPresets = async (modelName) => {
    try {
      const data = await modelService.getModelPresets(modelName);
      setModelPresets(data.presets || {});
      
      if (data.presets?.fast) {
        applyPreset('fast', data.presets.fast);
      }
      
      fetchAvailableParameters(modelName);
    } catch (error) {
      console.error('Error fetching model presets:', error);
    }
  };

  const fetchAvailableParameters = async (modelName) => {
    try {
      const data = await modelService.getModelParameters(modelName);
      setAvailableParameters(data.parameters || {});
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

  const toggleModelSelection = (modelName) => {
    if (useMultipleModels) {
      setSelectedModels(prev => {
        if (prev.includes(modelName)) {
          return prev.filter(m => m !== modelName);
        } else {
          return [...prev, modelName];
        }
      });
    } else {
      setSelectedModel(modelName);
    }
  };

  const clearModelSelection = () => {
    setSelectedModel('');
    setSelectedModels([]);
  };

  const fetchGallery = async () => {
    if (!clip?.id) return;
    
    try {
      const data = await clipService.getClipGallery(clip.id);
      setGallery(data);
      
      if (data.images?.length > 0 && !data.images.some(img => img.is_selected)) {
        selectContent(data.images[0].id, 'image');
      }
      if (data.videos?.length > 0 && !data.videos.some(vid => vid.is_selected)) {
        selectContent(response.data.videos[0].id, 'video');
      }
    } catch (error) {
      console.error('Error fetching gallery:', error);
    }
  };

  const handleGenerate = async () => {
    // Validate clip ID
    if (!isValidUUID(clip.id)) {
      toast.error('Invalid clip ID');
      return;
    }

    // Provider-specific prechecks
    if (provider === 'comfyui') {
      if (!isValidUUID(selectedServer)) {
        toast.error('Invalid server selection');
        return;
      }
      if (!selectedServer || (!selectedModel && selectedModels.length === 0)) {
        toast.error('Please select a server and at least one model');
        return;
      }
      if (!serverInfo?.is_online) {
        toast.error('Selected server is offline');
        return;
      }
    } else {
      // OpenAI provider: enforce video generation
      if (activeTab !== 'video') {
        setActiveTab('video');
      }
    }

    const prompt = sanitizeInput(prompts[activeTab]);
    const negativePrompt = sanitizeInput(prompts[`${activeTab}Negative`]);

    if (!prompt.trim()) {
      toast.error(`Please enter a ${activeTab} prompt`);
      return;
    }

    // Validate prompt length
    try {
      validatePromptLength(prompt);
      if (negativePrompt) {
        validatePromptLength(negativePrompt);
      }
    } catch (error) {
      toast.error(error.message);
      return;
    }

    setIsGenerating(true);

    try {
      // Prepare LoRAs data
      const lorasData = loras
        .filter(lora => lora.name !== 'none')
        .map(lora => ({ name: lora.name, weight: lora.weight }));

      // Build params
      const params = {
        ...generationParams,
        ...advancedParams,
        seed: generationParams.seed === -1 ? Math.floor(Math.random() * 1000000) : generationParams.seed,
        ...(provider === 'openai' ? { provider: 'openai' } : {}),
        ...(provider === 'openai' && soraReferenceImageUrl ? { input_reference_url: soraReferenceImageUrl } : {}),
      };

      // Validate generation parameters
      try {
        validateGenerationParams(params);
      } catch (error) {
        toast.error(error.message);
        setIsGenerating(false);
        return;
      }

      const isOpenAI = provider === 'openai';

      const requestData = {
        clip_id: clip.id,
        server_id: isOpenAI ? 'openai' : selectedServer,
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim(),
        model: isOpenAI ? (selectedModel || 'sora-2') : selectedModel,
        loras: isOpenAI ? [] : lorasData,
        generation_type: isOpenAI ? 'video' : activeTab,
        params,
      };

      let response;
      if (isOpenAI) {
        response = await generationService.generateV1(requestData);
      } else {
        response = await generationService.generate(requestData);
      }

      if (response?.job_id) {
        addTrackedJob({
          id: response.job_id,
          generation_type: isOpenAI ? 'video' : activeTab,
          status: 'pending',
          params: { prompt: prompt.trim() }
        });
      }

      toast.success(`${(isOpenAI || activeTab === 'video') ? 'Video' : 'Image'} generation started successfully`);

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
      await clipService.updateClipPrompts(clip.id, {
        image_prompt: prompts.image,
        video_prompt: prompts.video
      });
    } catch (error) {
      console.error('Error updating prompts:', error);
    }
  };

  const selectContent = async (contentId, contentType) => {
    try {
      await clipService.selectClipContent(clip.id, {
        content_id: contentId,
        content_type: contentType
      });
      
      toast.success(`Selected ${contentType}`);
      fetchGallery();
    } catch (error) {
      console.error('Error selecting content:', error);
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
  
  const updateLoraSearch = (index, value) => {
    const newQueries = [...loraSearchQueries];
    newQueries[index] = value;
    setLoraSearchQueries(newQueries);
  };

  const handleContentClick = (content) => {
    setSelectedContent(content);
    setShowMediaViewer(true);
  };
  
  // Get currently selected content for display
  const getSelectedContent = (type) => {
    const contentArray = gallery[type];
    if (!contentArray?.length) return null;
    
    // First try to find the selected one
    const selected = contentArray.find(item => item.is_selected);
    if (selected) return selected;
    
    // Fall back to the first item
    return contentArray[0];
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

      const data = await characterService.uploadFaceImage(formData);

      updateAdvancedParam('reactor_face_image', data.file_url);
      toast.success('Face image uploaded successfully');
    } catch (error) {
      console.error('Error uploading face image:', error);
    } finally {
      setIsUploadingFace(false);
    }
  };

  const handleReferenceUpload = async (event) => {
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

      const data = await characterService.uploadFaceImage(formData);

      setSoraReferenceImageUrl(data.file_url);
      toast.success('Reference image uploaded successfully');
    } catch (error) {
      console.error('Error uploading reference image:', error);
    } finally {
      setIsUploadingFace(false);
    }
  };

  const sendToPool = async (content, contentType) => {
    try {
      const clipData = await clipService.getClip(clip.id);
      const sceneData = await sceneService.getScene(clipData.scene_id);
      const project_id = sceneData.project_id;

      const poolData = {
        project_id: project_id,
        name: `${clip.name} - ${contentType}`,
        description: content.prompt || '',
        content_type: contentType,
        source_type: 'clip_generation',
        source_clip_id: clip.id,
        media_url: content.url,
        thumbnail_url: content.thumbnail_url || content.url,
        generation_params: {
          prompt: content.prompt,
          seed: content.seed,
          model: content.model_name || content.model,
          ...generationParams
        },
        tags: [contentType, selectedModel, clip.name],
        metadata: {
          clip_id: clip.id,
          clip_name: clip.name,
          generated_at: new Date().toISOString()
        }
      };

      await poolService.addToPool(poolData);
      toast.success('Sent to generation pool!');
    } catch (error) {
      console.error('Error sending to pool:', error);
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
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    sendToPool(content, contentType);
                  }}
                  className="w-full mt-2 h-7 text-xs hover:bg-indigo-600/20"
                >
                  <Database className="w-3 h-3 mr-1" />
                  Send to Pool
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!clip) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-7xl max-h-[90vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
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

        <div className="flex-1 overflow-hidden flex gap-4 min-h-0">
          <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          {showGallery ? (
            <div className="flex-1 flex gap-4 overflow-hidden">
              {/* Gallery Section - Left Side */}
              <div className="w-1/2 overflow-y-auto p-4 border-r border-panel">
                <div className="mb-4">
                  <h3 className="text-lg font-medium text-primary mb-2">Gallery</h3>
                  <Tabs value={activeTab} onValueChange={setActiveTab}>
                    <TabsList className="grid w-full grid-cols-2 bg-panel-dark">
                      <TabsTrigger value="image" className="data-[state=active]:bg-indigo-600">
                        <Image className="w-4 h-4 mr-2" />
                        Images ({gallery.images?.length || 0})
                      </TabsTrigger>
                      <TabsTrigger value="video" className="data-[state=active]:bg-indigo-600">
                        <Video className="w-4 h-4 mr-2" />
                        Videos ({gallery.videos?.length || 0})
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
                
                <Tabs value={activeTab} className="w-full">
                  <TabsContent value="image" className="mt-0">
                    {renderGallery(gallery.images, 'image')}
                  </TabsContent>
                  
                  <TabsContent value="video" className="mt-0">
                    {renderGallery(gallery.videos, 'video')}
                  </TabsContent>
                </Tabs>
              </div>
              
              {/* Selected Content Preview - Right Side */}
              <div className="w-1/2 overflow-y-auto p-4">
                <div className="mb-4">
                  <h3 className="text-lg font-medium text-primary">Current Selection</h3>
                </div>
                
                <div className="space-y-6">
                  {/* Current Image */}
                  <div>
                    <Label className="text-sm font-medium text-primary mb-2 block">
                      <Image className="w-4 h-4 mr-1 inline" />
                      Selected Image
                    </Label>
                    <div className="bg-panel-dark rounded-lg p-4 border border-panel">
                      {getSelectedContent('images') ? (
                        <div 
                          className="aspect-video bg-panel rounded mb-3 flex items-center justify-center cursor-pointer relative group"
                          onClick={() => handleContentClick(getSelectedContent('images'))}
                        >
                          <img 
                            src={getSelectedContent('images').url} 
                            alt="Selected" 
                            className="w-full h-full object-contain rounded"
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors rounded flex items-center justify-center">
                            <Eye className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        </div>
                      ) : (
                        <div className="aspect-video bg-panel rounded mb-3 flex items-center justify-center">
                          <p className="text-secondary text-sm">No image selected</p>
                        </div>
                      )}
                      
                      {getSelectedContent('images') && (
                        <div className="space-y-2">
                          <p className="text-xs text-secondary">
                            Prompt: {getSelectedContent('images').prompt}
                          </p>
                          {getSelectedContent('images').negative_prompt && (
                            <p className="text-xs text-secondary">
                              Negative: {getSelectedContent('images').negative_prompt}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Current Video */}
                  <div>
                    <Label className="text-sm font-medium text-primary mb-2 block">
                      <Video className="w-4 h-4 mr-1 inline" />
                      Selected Video
                    </Label>
                    <div className="bg-panel-dark rounded-lg p-4 border border-panel">
                      {getSelectedContent('videos') ? (
                        <div 
                          className="aspect-video bg-panel rounded mb-3 flex items-center justify-center cursor-pointer relative group"
                          onClick={() => handleContentClick(getSelectedContent('videos'))}
                        >
                          <video 
                            src={getSelectedContent('videos').url} 
                            className="w-full h-full object-contain rounded"
                            controls={false}
                            onMouseEnter={(e) => e.target.play()}
                            onMouseLeave={(e) => e.target.pause()}
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors rounded flex items-center justify-center">
                            <Eye className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        </div>
                      ) : (
                        <div className="aspect-video bg-panel rounded mb-3 flex items-center justify-center">
                          <p className="text-secondary text-sm">No video selected</p>
                        </div>
                      )}
                      
                      {getSelectedContent('videos') && (
                        <div className="space-y-2">
                          <p className="text-xs text-secondary">
                            Prompt: {getSelectedContent('videos').prompt}
                          </p>
                          {getSelectedContent('videos').negative_prompt && (
                            <p className="text-xs text-secondary">
                              Negative: {getSelectedContent('videos').negative_prompt}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
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

            {/* Provider Selection */}
            <div className="space-y-3">
              <Label className="text-sm font-medium text-primary">Provider</Label>
              <Select value={provider} onValueChange={setProvider}>
                <SelectTrigger className="form-input" data-testid="provider-select">
                  <SelectValue placeholder="Select provider" />
                </SelectTrigger>
                <SelectContent className="bg-panel border-panel">
                  <SelectItem value="comfyui" className="text-primary hover:bg-panel-dark">
                    ComfyUI (Servers)
                  </SelectItem>
                  <SelectItem value="openai" className="text-primary hover:bg-panel-dark">
                    OpenAI Sora (Video)
                  </SelectItem>
                </SelectContent>
              </Select>

              {/* Server Selection (ComfyUI only) */}
              {provider === 'comfyui' && (
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
                        <SelectValue placeholder="Select an online ComfyUI server" />
                      </SelectTrigger>
                      <SelectContent className="bg-panel border-panel">
                        {getOnlineServers().length === 0 ? (
                          <div className="px-2 py-4 text-center text-secondary text-sm">
                            No online servers available
                          </div>
                        ) : (
                          getOnlineServers().map((server) => (
                            <SelectItem key={server.id} value={server.id}>
                              <div className="flex items-center space-x-2">
                                <span>{server.name}</span>
                                <Badge variant="outline" className="text-xs">
                                  {server.url}
                                </Badge>
                                {serverInfo?.id === server.id && serverInfo?.is_online && (
                                  <Badge className="bg-green-500 text-white text-xs">Online</Badge>
                                )}
                              </div>
                            </SelectItem>
                          ))
                        )}
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
              )}
            </div>

              {(provider === 'openai' || serverInfo?.is_online) && (
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

                  {/* Reference Image (OpenAI Sora - optional first frame) */}
                  {provider === 'openai' && activeTab === 'video' && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-primary">Reference Image (First Frame - optional)</Label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleReferenceUpload}
                          className="hidden"
                          id="sora-reference-upload"
                          data-testid="sora-reference-upload-input"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => document.getElementById('sora-reference-upload')?.click()}
                          disabled={isUploadingFace}
                          className="btn-secondary"
                          data-testid="sora-reference-upload-btn"
                        >
                          {isUploadingFace ? 'Uploading...' : 'Upload Reference Image'}
                        </Button>
                        {soraReferenceImageUrl && (
                          <Badge variant="outline" className="text-xs">✓ Reference added</Badge>
                        )}
                      </div>
                      <div className="space-y-2">
                        <Label className="text-xs text-secondary">Or enter reference image URL</Label>
                        <Input
                          className="form-input text-sm"
                          placeholder="/uploads/your-image.webp or full http(s) URL"
                          value={soraReferenceImageUrl}
                          onChange={(e) => setSoraReferenceImageUrl(e.target.value)}
                          data-testid="sora-reference-url-input"
                        />
                        <div className="text-xs text-secondary">
                          Tip: For best results, use the same resolution as your target video size.
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Model Selection */}
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-primary flex items-center">
                        <Cpu className="w-4 h-4 mr-1" />
                        Model ({filteredModels.length} available)
                        {modelDefaults.detected_type && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            {modelDefaults.detected_type}
                          </Badge>
                        )}
                      </Label>

                      {/* Multiple Model Toggle */}
                      <div className="flex items-center space-x-2">
                        <Switch
                          checked={useMultipleModels}
                          onCheckedChange={(checked) => {
                            setUseMultipleModels(checked);
                            if (checked) {
                              setSelectedModels(selectedModel ? [selectedModel] : []);
                              setSelectedModel('');
                            } else {
                              setSelectedModel(selectedModels.length > 0 ? selectedModels[0] : '');
                              setSelectedModels([]);
                            }
                          }}
                          data-testid="multiple-models-toggle"
                        />
                        <Label className="text-xs text-secondary">Select multiple models</Label>
                        {(selectedModels.length > 0 || selectedModel) && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={clearModelSelection}
                            className="h-6 px-2 text-xs"
                          >
                            <X className="w-3 h-3 mr-1" />
                            Clear
                          </Button>
                        )}
                      </div>

                      {/* Selected Models Display */}
                      {useMultipleModels && selectedModels.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {selectedModels.map(model => (
                            <Badge
                              key={model}
                              variant="secondary"
                              className="text-xs cursor-pointer hover:bg-red-500/20"
                              onClick={() => toggleModelSelection(model)}
                            >
                              {model}
                              <X className="w-3 h-3 ml-1" />
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* Model selection varies by provider */}
                      {provider === 'openai' ? (
                        <Select value={selectedModel} onValueChange={setSelectedModel}>
                          <SelectTrigger className="form-input">
                            <SelectValue placeholder="Select Sora model" />
                          </SelectTrigger>
                          <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                            <SelectItem value="sora-2" className="text-primary hover:bg-panel-dark">
                              <span>sora-2 (faster)</span>
                            </SelectItem>
                            <SelectItem value="sora-2-pro" className="text-primary hover:bg-panel-dark">
                              <span>sora-2-pro (higher fidelity)</span>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <>
                        {/* Model Search Input */}
                        <div className="relative">
                          <Input
                            placeholder="Search models..."
                            value={modelSearchQuery}
                            onChange={(e) => setModelSearchQuery(e.target.value)}
                            className="form-input pr-8"
                          />
                          {modelSearchQuery && (
                            <button
                              onClick={() => setModelSearchQuery('')}
                              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-secondary hover:text-primary"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          )}
                        </div>

                        <Select
                          value={useMultipleModels ? "" : selectedModel}
                          onValueChange={(value) => {
                            if (useMultipleModels) {
                              toggleModelSelection(value);
                            } else {
                              setSelectedModel(value);
                            }
                          }}
                        >
                          <SelectTrigger className="form-input" data-testid="model-select">
                            <SelectValue placeholder={useMultipleModels ? "Select models..." : "Select model"} />
                          </SelectTrigger>
                          <SelectContent className="bg-panel border-panel max-h-64 overflow-y-auto">
                            {filteredModels.length === 0 ? (
                              <div className="px-2 py-4 text-center text-secondary text-sm">
                                {modelSearchQuery ? 'No models match your search' : 'No models available'}
                              </div>
                            ) : (
                              filteredModels.map((model, index) => (
                                <SelectItem
                                  key={index}
                                  value={model.name}
                                  className={`text-primary hover:bg-panel-dark ${
                                    (useMultipleModels && selectedModels.includes(model.name)) ||
                                    (!useMultipleModels && selectedModel === model.name)
                                      ? 'bg-indigo-500/20' : ''
                                  }`}
                                >
                                  <div className="flex items-center justify-between w-full">
                                    <span>{model.name}</span>
                                    {((useMultipleModels && selectedModels.includes(model.name)) ||
                                      (!useMultipleModels && selectedModel === model.name)) && (
                                      <div className="w-2 h-2 bg-indigo-500 rounded-full ml-2" />
                                    )}
                                  </div>
                                </SelectItem>
                              ))
                            )}
                          </SelectContent>
                        </Select>
                        </>
                      )}
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
                    
                    {/* Multiple LoRAs (ComfyUI only) */}
                    {provider === 'comfyui' && (
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
                        {loras.map((lora, index) => {
                          const filteredLoras = getFilteredLoras(index);
                          return (
                          <div key={index} className="flex flex-col space-y-2">
                            <div className="flex items-center space-x-2">
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
                                  {filteredLoras.length === 0 ? (
                                    <div className="px-2 py-4 text-center text-secondary text-sm">
                                      {loraSearchQueries[index] ? 'No LoRAs match your search' : 'No LoRAs available'}
                                    </div>
                                  ) : (
                                    filteredLoras.map((availableLora, loraIndex) => (
                                      <SelectItem
                                        key={loraIndex}
                                        value={availableLora.name}
                                        className={`text-primary hover:bg-panel-dark ${
                                          lora.name === availableLora.name ? 'bg-indigo-500/20' : ''
                                        }`}
                                      >
                                        <div className="flex items-center justify-between w-full">
                                          <span>{availableLora.name}</span>
                                          {lora.name === availableLora.name && (
                                            <div className="w-2 h-2 bg-indigo-500 rounded-full ml-2" />
                                          )}
                                        </div>
                                      </SelectItem>
                                    ))
                                  )}
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
                            {/* LoRA Search Input */}
                            {serverInfo?.loras?.length > 10 && (
                              <div className="relative ml-2">
                                <Input
                                  placeholder="Search LoRAs..."
                                  value={loraSearchQueries[index] || ''}
                                  onChange={(e) => updateLoraSearch(index, e.target.value)}
                                  className="form-input pr-8 text-sm h-8"
                                />
                                {loraSearchQueries[index] && (
                                  <button
                                    onClick={() => updateLoraSearch(index, '')}
                                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-secondary hover:text-primary"
                                  >
                                    <X className="w-3 h-3" />
                                  </button>
                                )}
                              </div>
                            )}
                          </div>
                          );
                        })}
                      </div>
                    </div>
                    )}
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
                                    {filteredModels.map((model, index) => (
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

                        {/* Custom Workflow (ComfyUI only) */}
                        {provider === 'comfyui' && (
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
                        )}
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
                disabled={
                  isGenerating ||
                  !prompts[activeTab].trim() ||
                  (provider === 'comfyui' && (!selectedServer || !serverInfo?.is_online))
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
                    Generate {activeTab}
                  </>
                )}
              </Button>
            </div>
          )}
          </div>

          {/* Results Preview Panel - Right Side */}
          <div className="w-80 flex-shrink-0 overflow-hidden">
            <ResultsPreviewPanel
              clipId={clip?.id}
              contentType={activeTab === 'image' ? 'image' : activeTab === 'video' ? 'video' : 'all'}
              limit={3}
              onContentClick={handleContentClick}
            />
          </div>
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