import React, { useState, useEffect } from 'react';
import { Wand2, Image, Video, Server, Settings, Cpu, Zap, Eye, Grid, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import axios from 'axios';

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
    } catch (error) {
      console.error('Error fetching server info:', error);
      toast.error('Failed to fetch server info');
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
      const requestData = {
        clip_id: clip.id,
        server_id: selectedServer,
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim(),
        model: selectedModel,
        lora: selectedLora && selectedLora !== "none" ? selectedLora : null,
        generation_type: activeTab,
        params: {
          ...generationParams,
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
              <div className="aspect-square bg-panel-dark rounded mb-2 flex items-center justify-center">
                {content.url ? (
                  contentType === 'image' ? (
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
                  )
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
                  <div className="grid grid-cols-2 gap-4">
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
                    
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-primary">LoRA (Optional)</Label>
                      <Select value={selectedLora} onValueChange={setSelectedLora}>
                        <SelectTrigger className="form-input" data-testid="lora-select">
                          <SelectValue placeholder="Select LoRA" />
                        </SelectTrigger>
                        <SelectContent className="bg-panel border-panel max-h-48 overflow-y-auto">
                          <SelectItem value="none" className="text-primary hover:bg-panel-dark">
                            None
                          </SelectItem>
                          {serverInfo.loras.map((lora, index) => (
                            <SelectItem 
                              key={index} 
                              value={lora.name} 
                              className="text-primary hover:bg-panel-dark"
                            >
                              {lora.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Generation Parameters */}
                  <Card className="glass-panel">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-primary text-sm flex items-center">
                        <Settings className="w-4 h-4 mr-2" />
                        Generation Parameters
                        {modelDefaults.detected_type && (
                          <span className="ml-2 text-xs text-secondary">
                            (Optimized for {modelDefaults.detected_type})
                          </span>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
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
                    </CardContent>
                  </Card>
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
      </DialogContent>
    </Dialog>
  );
};

export default EnhancedGenerationDialog;