import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { comfyuiService, generationService } from '@/services';
import { useNotifications } from '@/contexts/NotificationContext';
import {
  Wand2,
  Loader2,
  CheckCircle2,
  Image as ImageIcon,
  Video,
  Server,
  Layers,
  AlertCircle
} from 'lucide-react';

const BatchGenerationDialog = ({
  open,
  onOpenChange,
  clips = [],
  servers = [],
  selectedClipIds: propSelectedClipIds = [],
  onBatchStart
}) => {
  const { addTrackedJob } = useNotifications();

  const [selectedClipIds, setSelectedClipIds] = useState([]);
  const [generationType, setGenerationType] = useState('image');
  const [selectedServer, setSelectedServer] = useState('');
  const [serverInfo, setServerInfo] = useState(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [steps, setSteps] = useState(20);
  const [cfgScale, setCfgScale] = useState(7);
  const [width, setWidth] = useState(512);
  const [height, setHeight] = useState(512);
  const [seed, setSeed] = useState(-1);
  const [loading, setLoading] = useState(false);

  // Fetch server info when server is selected
  useEffect(() => {
    if (selectedServer) {
      fetchServerInfo(selectedServer);
    }
  }, [selectedServer]);

  const fetchServerInfo = async (serverId) => {
    try {
      const data = await comfyuiService.getServer(serverId);
      setServerInfo(data);

      if (data.models && data.models.length > 0 && !selectedModel) {
        setSelectedModel(data.models[0].name);
      }
    } catch (error) {
      console.error('Error fetching server info:', error);
    }
  };

  // Pre-select clips when dialog opens with selectedClipIds prop
  useEffect(() => {
    if (open && propSelectedClipIds.length > 0) {
      setSelectedClipIds(propSelectedClipIds);
    }
  }, [open, propSelectedClipIds]);


  const getOnlineServers = () => {
    return servers.filter(server => server.is_active !== false);
  };

  const toggleClipSelection = (clipId) => {
    setSelectedClipIds(prev =>
      prev.includes(clipId)
        ? prev.filter(id => id !== clipId)
        : [...prev, clipId]
    );
  };

  const selectAllClips = () => {
    setSelectedClipIds(clips.map(clip => clip.id));
  };

  const deselectAllClips = () => {
    setSelectedClipIds([]);
  };

  const handleBatchGenerate = async () => {
    if (selectedClipIds.length === 0) {
      toast.error('Please select at least one clip');
      return;
    }

    if (!selectedServer) {
      toast.error('Please select a server');
      return;
    }

    if (!selectedModel) {
      toast.error('Please select a model');
      return;
    }

    setLoading(true);

    try {
      const params = {
        steps,
        cfg_scale: cfgScale,
        width,
        height,
        seed
      };

      const response = await generationService.generateBatch({
        clip_ids: selectedClipIds,
        server_id: selectedServer,
        generation_type: generationType,
        prompt: prompt || undefined,
        negative_prompt: negativePrompt || undefined,
        model: selectedModel,
        params,
        loras: []
      });

      if (response?.job_ids) {
        response.job_ids.forEach(jobId => {
          addTrackedJob({
            id: jobId,
            generation_type: generationType,
            status: 'pending',
            params: { prompt: prompt || '' }
          });
        });
      }

      toast.success(`Batch generation started for ${selectedClipIds.length} clips`);

      // Notify parent and close dialog
      if (onBatchStart) {
        onBatchStart(response);
      }

      onOpenChange(false);

      // Reset form
      setSelectedClipIds([]);
      setPrompt('');
      setNegativePrompt('');
    } catch (error) {
      console.error('Error starting batch generation:', error);
      toast.error(error.response?.data?.detail || 'Failed to start batch generation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-primary flex items-center space-x-2">
            <Layers className="w-5 h-5" />
            <span>Batch Generation</span>
          </DialogTitle>
          <DialogDescription className="text-secondary">
            Generate images or videos for multiple clips simultaneously
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-6">
          {/* Clip Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-primary">
                Select Clips ({selectedClipIds.length} selected)
              </Label>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={selectAllClips}
                  className="h-7 text-xs"
                >
                  Select All
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={deselectAllClips}
                  className="h-7 text-xs"
                  disabled={selectedClipIds.length === 0}
                >
                  Deselect All
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-2 bg-panel-dark rounded-lg border border-panel">
              {clips.length === 0 ? (
                <div className="col-span-2 text-center py-8 text-secondary">
                  No clips available
                </div>
              ) : (
                clips.map((clip) => (
                  <div
                    key={clip.id}
                    className={`flex items-start space-x-2 p-3 rounded-lg border transition-all cursor-pointer ${
                      selectedClipIds.includes(clip.id)
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-panel hover:border-indigo-500/50'
                    }`}
                    onClick={() => toggleClipSelection(clip.id)}
                  >
                    <Checkbox
                      checked={selectedClipIds.includes(clip.id)}
                      onCheckedChange={() => toggleClipSelection(clip.id)}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-primary truncate">
                        {clip.name}
                      </div>
                      <div className="text-xs text-secondary truncate">
                        {clip.lyrics || 'No lyrics'}
                      </div>
                      <div className="text-xs text-secondary mt-1">
                        {clip.length}s • Position: {clip.timeline_position}s
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Generation Type */}
          <div className="space-y-2">
            <Label className="text-primary">Generation Type</Label>
            <Tabs value={generationType} onValueChange={setGenerationType}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="image" className="flex items-center space-x-2">
                  <ImageIcon className="w-4 h-4" />
                  <span>Image</span>
                </TabsTrigger>
                <TabsTrigger value="video" className="flex items-center space-x-2">
                  <Video className="w-4 h-4" />
                  <span>Video</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Server Selection */}
          <div className="space-y-2">
            <Label className="text-primary flex items-center space-x-2">
              <Server className="w-4 h-4" />
              <span>ComfyUI Server</span>
            </Label>
            <Select value={selectedServer} onValueChange={setSelectedServer}>
              <SelectTrigger>
                <SelectValue placeholder="Select an online ComfyUI server" />
              </SelectTrigger>
              <SelectContent>
                {getOnlineServers().length === 0 ? (
                  <div className="px-2 py-4 text-center text-secondary text-sm">
                    No online servers available
                  </div>
                ) : (
                  getOnlineServers().map((server) => (
                    <SelectItem key={server.id} value={server.id}>
                      <div className="flex items-center space-x-2">
                        <span>{server.name}</span>
                        {serverInfo?.id === server.id && serverInfo?.is_online && (
                          <Badge className="bg-green-500">Online</Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          {/* Model Selection */}
          {selectedServer && (
            <div className="space-y-2">
              <Label className="text-primary">
                Model ({serverInfo?.models?.length || 0} available)
              </Label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent className="max-h-64 overflow-y-auto">
                  {!serverInfo?.models || serverInfo.models.length === 0 ? (
                    <div className="px-2 py-4 text-center text-secondary text-sm">
                      No models available
                    </div>
                  ) : (
                    serverInfo.models
                      .sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()))
                      .map((model, index) => (
                        <SelectItem key={index} value={model.name}>
                          {model.name}
                        </SelectItem>
                      ))
                  )}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Prompts */}
          <div className="space-y-2">
            <Label className="text-primary">
              Prompt (Optional - will use clip prompts if empty)
            </Label>
            <Textarea
              placeholder="Enter generation prompt or leave empty to use individual clip prompts..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-20"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-primary">Negative Prompt</Label>
            <Textarea
              placeholder="Enter negative prompt..."
              value={negativePrompt}
              onChange={(e) => setNegativePrompt(e.target.value)}
              className="min-h-16"
            />
          </div>

          {/* Parameters */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-primary">Steps</Label>
              <Input
                type="number"
                value={steps}
                onChange={(e) => setSteps(parseInt(e.target.value))}
                min="1"
                max="150"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-primary">CFG Scale</Label>
              <Input
                type="number"
                value={cfgScale}
                onChange={(e) => setCfgScale(parseFloat(e.target.value))}
                min="1"
                max="30"
                step="0.1"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-primary">Width</Label>
              <Input
                type="number"
                value={width}
                onChange={(e) => setWidth(parseInt(e.target.value))}
                min="64"
                max="2048"
                step="8"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-primary">Height</Label>
              <Input
                type="number"
                value={height}
                onChange={(e) => setHeight(parseInt(e.target.value))}
                min="64"
                max="2048"
                step="8"
              />
            </div>

            <div className="space-y-2 col-span-2">
              <Label className="text-primary">Seed (-1 for random)</Label>
              <Input
                type="number"
                value={seed}
                onChange={(e) => setSeed(parseInt(e.target.value))}
              />
            </div>
          </div>

          {/* Warning */}
          {selectedClipIds.length > 5 && (
            <div className="flex items-start space-x-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-200">
                You are about to generate content for {selectedClipIds.length} clips.
                This may take some time and consume significant server resources.
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-panel">
          <div className="text-sm text-secondary">
            {selectedClipIds.length} clip{selectedClipIds.length !== 1 ? 's' : ''} selected
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleBatchGenerate}
              disabled={loading || selectedClipIds.length === 0 || !selectedServer || !selectedModel}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Wand2 className="w-4 h-4 mr-2" />
                  Start Batch Generation
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BatchGenerationDialog;
