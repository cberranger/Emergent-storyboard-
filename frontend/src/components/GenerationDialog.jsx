import React, { useState, useEffect } from 'react';
import { Wand2, Image, Video, Server, Settings, Cpu, Zap } from 'lucide-react';
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

const GenerationDialog = ({ open, onOpenChange, clip, servers, onGenerated }) => {
  const [selectedServer, setSelectedServer] = useState('');
  const [serverInfo, setServerInfo] = useState(null);
  const [generationType, setGenerationType] = useState('image');
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedLora, setSelectedLora] = useState('none');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationParams, setGenerationParams] = useState({
    steps: 20,
    cfg: 8,
    width: 512,
    height: 512,
    seed: -1
  });

  useEffect(() => {
    if (clip && open) {
      // Pre-fill prompt with clip lyrics or name
      const initialPrompt = clip.lyrics || clip.name || '';
      setPrompt(initialPrompt);
    }
  }, [clip, open]);

  useEffect(() => {
    if (selectedServer) {
      fetchServerInfo(selectedServer);
    }
  }, [selectedServer]);

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

  const handleGenerate = async () => {
    if (!selectedServer || !prompt.trim()) {
      toast.error('Please select a server and enter a prompt');
      return;
    }

    if (!serverInfo?.is_online) {
      toast.error('Selected server is offline');
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
        generation_type: generationType,
        params: {
          ...generationParams,
          seed: generationParams.seed === -1 ? Math.floor(Math.random() * 1000000) : generationParams.seed
        }
      };

      await axios.post(`${API}/generate`, requestData);
      
      toast.success(`${generationType === 'image' ? 'Image' : 'Video'} generation started successfully`);
      onGenerated();
      onOpenChange(false);
    } catch (error) {
      console.error('Error generating content:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to generate content';
      toast.error(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const updateParam = (key, value) => {
    setGenerationParams(prev => ({
      ...prev,
      [key]: parseFloat(value) || value
    }));
  };

  if (!clip) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-4xl max-h-[85vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="text-primary flex items-center">
            <Wand2 className="w-5 h-5 mr-2" />
            Generate Content for "{clip.name}"
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col space-y-6 overflow-y-auto max-h-[70vh] pr-2">
          {/* Server Selection */}
          <div className="space-y-3">
            <Label className="text-sm font-medium text-primary">ComfyUI Server</Label>
            {servers.length === 0 ? (
              <div className="text-center py-8 bg-panel-dark rounded-lg border border-panel">
                <Server className="w-8 h-8 text-secondary mx-auto mb-2" />
                <p className="text-secondary text-sm">No servers configured</p>
                <p className="text-xs text-secondary mt-1">Add a ComfyUI server to start generating</p>
              </div>
            ) : (
              <Select value={selectedServer} onValueChange={setSelectedServer}>
                <SelectTrigger className="form-input" data-testid="server-select">
                  <SelectValue placeholder="Select a ComfyUI server" />
                </SelectTrigger>
                <SelectContent className="bg-panel border-panel">
                  {servers.map((server) => (
                    <SelectItem key={server.id} value={server.id} className="text-primary hover:bg-panel-dark">
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
            )}
            
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
          </div>

          {serverInfo?.is_online && (
            <>
              {/* Generation Type */}
              <div className="space-y-3">
                <Label className="text-sm font-medium text-primary">Generation Type</Label>
                <Tabs value={generationType} onValueChange={setGenerationType} className="w-full">
                  <TabsList className="grid w-full grid-cols-2 bg-panel-dark">
                    <TabsTrigger 
                      value="image" 
                      className="data-[state=active]:bg-indigo-600 flex items-center"
                      data-testid="image-tab"
                    >
                      <Image className="w-4 h-4 mr-2" />
                      Image
                    </TabsTrigger>
                    <TabsTrigger 
                      value="video" 
                      className="data-[state=active]:bg-indigo-600 flex items-center"
                      disabled
                      data-testid="video-tab"
                    >
                      <Video className="w-4 h-4 mr-2" />
                      Video (Coming Soon)
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Prompts */}
              <div className="grid grid-cols-1 gap-4">
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-primary">Positive Prompt</Label>
                  <Textarea
                    className="form-input min-h-[80px]"
                    placeholder="Describe what you want to generate..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    data-testid="positive-prompt-input"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-primary">Negative Prompt</Label>
                  <Textarea
                    className="form-input min-h-[60px]"
                    placeholder="Describe what you don't want..."
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    data-testid="negative-prompt-input"
                  />
                </div>
              </div>

              {/* Model Selection */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-primary flex items-center">
                    <Cpu className="w-4 h-4 mr-1" />
                    Model
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
                          {[512, 768, 1024, 1280].map(size => (
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
                          {[512, 768, 1024, 1280].map(size => (
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

              {/* Action Buttons */}
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
                  disabled={isGenerating || !selectedServer || !prompt.trim() || !serverInfo?.is_online}
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
                      Generate {generationType}
                    </>
                  )}
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default GenerationDialog;