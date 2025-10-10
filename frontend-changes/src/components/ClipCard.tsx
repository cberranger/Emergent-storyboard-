import { useState } from 'react';
import { GenerationPanel } from './GenerationPanel';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';
import { Play, Image, Video, Sparkles, MoreVertical } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

interface Clip {
  id: string;
  startTime: number;
  duration: number;
  imagePrompt: string;
  videoPrompt: string;
  currentVersion: number;
  versions: Array<{ id: number; generations: any[] }>;
  generations: Array<{ id: string; type: string; url: string; status: string }>;
}

export function ClipCard({ clip, clipIndex }: { clip: Clip; clipIndex: number }) {
  const [showGenerationPanel, setShowGenerationPanel] = useState(false);

  const imageGens = clip.generations.filter(g => g.type === 'image');
  const videoGens = clip.generations.filter(g => g.type === 'video');

  return (
    <>
      <Card 
        className="bg-neutral-800 border-neutral-700 hover:border-violet-500 transition-colors cursor-pointer overflow-hidden group"
        onClick={() => setShowGenerationPanel(true)}
      >
        {/* Thumbnail Preview */}
        <div className="aspect-video bg-neutral-900 relative overflow-hidden">
          {imageGens.length > 0 ? (
            <div className="w-full h-full bg-gradient-to-br from-violet-900/20 to-purple-900/20 flex items-center justify-center">
              <Play className="w-12 h-12 text-white/20" />
            </div>
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-neutral-800 to-neutral-900 flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-neutral-600" />
            </div>
          )}
          
          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <Button size="sm" variant="secondary">
              Open Editor
            </Button>
          </div>

          {/* Generation Count Badge */}
          <div className="absolute top-2 right-2 flex gap-1">
            {imageGens.length > 0 && (
              <Badge className="bg-blue-600 text-white text-xs">
                <Image className="w-3 h-3 mr-1" />
                {imageGens.length}
              </Badge>
            )}
            {videoGens.length > 0 && (
              <Badge className="bg-purple-600 text-white text-xs">
                <Video className="w-3 h-3 mr-1" />
                {videoGens.length}
              </Badge>
            )}
          </div>
        </div>

        {/* Clip Info */}
        <div className="p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-neutral-400">Clip {clipIndex + 1}</span>
            <div className="flex items-center gap-1">
              <Select value={clip.currentVersion.toString()}>
                <SelectTrigger className="w-20 h-6 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {clip.versions.map((version) => (
                    <SelectItem key={version.id} value={version.id.toString()}>
                      V{version.id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <DropdownMenu>
                <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <MoreVertical className="w-3 h-3" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>New Version</DropdownMenuItem>
                  <DropdownMenuItem>Duplicate</DropdownMenuItem>
                  <DropdownMenuItem className="text-red-500">Delete</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <Image className="w-3 h-3 mt-0.5 text-blue-400 shrink-0" />
              <p className="text-xs text-neutral-300 line-clamp-2">{clip.imagePrompt}</p>
            </div>
            <div className="flex items-start gap-2">
              <Video className="w-3 h-3 mt-0.5 text-purple-400 shrink-0" />
              <p className="text-xs text-neutral-300 line-clamp-2">{clip.videoPrompt}</p>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-neutral-700 flex items-center justify-between">
            <Badge variant="outline" className="text-xs">
              {clip.duration}s
            </Badge>
            <Button 
              size="sm" 
              className="h-7 text-xs bg-violet-600 hover:bg-violet-700"
              onClick={(e) => {
                e.stopPropagation();
                setShowGenerationPanel(true);
              }}
            >
              <Sparkles className="w-3 h-3 mr-1" />
              Generate
            </Button>
          </div>
        </div>
      </Card>

      {/* Generation Panel Sheet */}
      <Sheet open={showGenerationPanel} onOpenChange={setShowGenerationPanel}>
        <SheetContent side="right" className="w-full sm:max-w-2xl bg-neutral-900 border-neutral-800 overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Clip {clipIndex + 1} - Generation Studio</SheetTitle>
          </SheetHeader>
          <GenerationPanel clip={clip} />
        </SheetContent>
      </Sheet>
    </>
  );
}
