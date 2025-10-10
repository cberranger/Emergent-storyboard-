import { useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Slider } from './ui/slider';
import { Separator } from './ui/separator';
import { Image, Video, Sparkles, Download, Trash2, Server } from 'lucide-react';

interface Clip {
  id: string;
  imagePrompt: string;
  videoPrompt: string;
  generations: Array<{ id: string; type: string; url: string; status: string }>;
}

// Mock ComfyUI servers
const mockServers = [
  { id: 'server-1', name: 'GPU Server 1', status: 'online', models: ['SD XL', 'SD 1.5'] },
  { id: 'server-2', name: 'GPU Server 2', status: 'online', models: ['AnimateDiff', 'SVD'] },
  { id: 'server-3', name: 'GPU Server 3', status: 'busy', models: ['SD XL', 'AnimateDiff'] }
];

const mockModels = ['SD XL Turbo', 'SD XL 1.0', 'SD 1.5', 'AnimateDiff v3', 'SVD 1.1'];
const mockLoras = ['Cinematic', 'Film Grain', 'Studio Ghibli', 'Photorealistic', 'Comic Book'];

export function GenerationPanel({ clip }: { clip: Clip }) {
  const [imagePrompt, setImagePrompt] = useState(clip.imagePrompt);
  const [videoPrompt, setVideoPrompt] = useState(clip.videoPrompt);
  const [selectedServer, setSelectedServer] = useState('server-1');
  const [selectedModel, setSelectedModel] = useState('SD XL Turbo');
  const [selectedLoras, setSelectedLoras] = useState<string[]>([]);
  const [steps, setSteps] = useState([25]);
  const [cfg, setCfg] = useState([7]);

  return (
    <div className="space-y-6 py-6">
      <Tabs defaultValue="prompts" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="prompts">Prompts</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="gallery">Gallery</TabsTrigger>
        </TabsList>

        <TabsContent value="prompts" className="space-y-4">
          {/* Image Prompt */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Image className="w-4 h-4 text-blue-400" />
              Image Prompt
            </Label>
            <Textarea
              value={imagePrompt}
              onChange={(e) => setImagePrompt(e.target.value)}
              className="min-h-[100px] bg-neutral-800 border-neutral-700"
              placeholder="Describe the image you want to generate..."
            />
          </div>

          {/* Video Prompt */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Video className="w-4 h-4 text-purple-400" />
              Video Prompt (Motion)
            </Label>
            <Textarea
              value={videoPrompt}
              onChange={(e) => setVideoPrompt(e.target.value)}
              className="min-h-[100px] bg-neutral-800 border-neutral-700"
              placeholder="Describe the motion and animation..."
            />
          </div>

          <Button className="w-full bg-violet-600 hover:bg-violet-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Generate Both
          </Button>
        </TabsContent>

        <TabsContent value="config" className="space-y-4">
          {/* ComfyUI Server Selection */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Server className="w-4 h-4" />
              ComfyUI Server
            </Label>
            <Select value={selectedServer} onValueChange={setSelectedServer}>
              <SelectTrigger className="bg-neutral-800 border-neutral-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {mockServers.map((server) => (
                  <SelectItem key={server.id} value={server.id}>
                    <div className="flex items-center gap-2">
                      <span>{server.name}</span>
                      <Badge
                        variant={server.status === 'online' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {server.status}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Separator className="bg-neutral-800" />

          {/* Model Selection */}
          <div className="space-y-2">
            <Label>Model</Label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="bg-neutral-800 border-neutral-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {mockModels.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* LoRA Selection */}
          <div className="space-y-2">
            <Label>LoRAs</Label>
            <div className="flex flex-wrap gap-2">
              {mockLoras.map((lora) => (
                <Badge
                  key={lora}
                  variant={selectedLoras.includes(lora) ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => {
                    setSelectedLoras(prev =>
                      prev.includes(lora)
                        ? prev.filter(l => l !== lora)
                        : [...prev, lora]
                    );
                  }}
                >
                  {lora}
                </Badge>
              ))}
            </div>
          </div>

          <Separator className="bg-neutral-800" />

          {/* Steps */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>Steps</Label>
              <span className="text-sm text-neutral-400">{steps[0]}</span>
            </div>
            <Slider
              value={steps}
              onValueChange={setSteps}
              min={10}
              max={50}
              step={1}
              className="w-full"
            />
          </div>

          {/* CFG Scale */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>CFG Scale</Label>
              <span className="text-sm text-neutral-400">{cfg[0]}</span>
            </div>
            <Slider
              value={cfg}
              onValueChange={setCfg}
              min={1}
              max={20}
              step={0.5}
              className="w-full"
            />
          </div>

          <Button className="w-full bg-violet-600 hover:bg-violet-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Generate with Settings
          </Button>
        </TabsContent>

        <TabsContent value="gallery" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-neutral-400">
              {clip.generations.length} generations
            </div>
            <Button variant="outline" size="sm">
              Generate More
            </Button>
          </div>

          <ScrollArea className="h-[500px]">
            <div className="grid grid-cols-2 gap-3">
              {clip.generations.length > 0 ? (
                clip.generations.map((gen) => (
                  <Card key={gen.id} className="bg-neutral-800 border-neutral-700 overflow-hidden group">
                    <div className="aspect-video bg-gradient-to-br from-violet-900/20 to-purple-900/20 relative">
                      <div className="absolute inset-0 flex items-center justify-center">
                        {gen.type === 'image' ? (
                          <Image className="w-12 h-12 text-white/20" />
                        ) : (
                          <Video className="w-12 h-12 text-white/20" />
                        )}
                      </div>
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <Button size="sm" variant="secondary">
                          <Download className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      <Badge className="absolute top-2 right-2 text-xs">
                        {gen.type}
                      </Badge>
                    </div>
                  </Card>
                ))
              ) : (
                <div className="col-span-2 text-center py-12 text-neutral-500">
                  <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No generations yet</p>
                  <p className="text-sm mt-1">Click generate to create content</p>
                </div>
              )}

              {/* Add more placeholder cards */}
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={`placeholder-${i}`} className="bg-neutral-800 border-neutral-700 border-dashed opacity-50">
                  <div className="aspect-video flex items-center justify-center">
                    <Sparkles className="w-8 h-8 text-neutral-600" />
                  </div>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}
