import { useState } from 'react';
import { ClipCard } from './ClipCard';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { ChevronDown, ChevronRight, Edit2, Plus, Copy, Trash2, MoreVertical } from 'lucide-react';
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

interface Scene {
  id: string;
  description: string;
  startTime: number;
  duration: number;
  currentVersion: number;
  versions: Array<{ id: number; name: string; thumbnail: string }>;
  clips: any[];
}

export function SceneCard({ scene, sceneIndex, zoom }: { scene: Scene; sceneIndex: number; zoom: number }) {
  const [expanded, setExpanded] = useState(true);
  const [editing, setEditing] = useState(false);
  const [description, setDescription] = useState(scene.description);

  return (
    <Card className="bg-neutral-900 border-neutral-800 overflow-hidden">
      {/* Scene Header */}
      <div className="bg-gradient-to-r from-violet-600/20 to-purple-600/20 border-b border-neutral-800">
        <div className="p-4 flex items-start gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 shrink-0"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-sm">Scene {sceneIndex + 1}</h3>
              <Badge variant="outline" className="text-xs">
                {scene.duration}s
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {scene.clips.length} clips
              </Badge>
              
              <Select value={scene.currentVersion.toString()}>
                <SelectTrigger className="w-32 h-7 text-xs ml-auto">
                  <SelectValue placeholder="Version" />
                </SelectTrigger>
                <SelectContent>
                  {scene.versions.map((version) => (
                    <SelectItem key={version.id} value={version.id.toString()}>
                      {version.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {editing ? (
              <div className="flex gap-2">
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="flex-1 min-h-[60px] bg-neutral-800 border-neutral-700 text-sm"
                  placeholder="Scene description..."
                />
                <div className="flex flex-col gap-1">
                  <Button
                    size="sm"
                    onClick={() => setEditing(false)}
                    className="h-7"
                  >
                    Save
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setDescription(scene.description);
                      setEditing(false);
                    }}
                    className="h-7"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex items-start gap-2">
                <p className="text-sm text-neutral-300 flex-1">{description}</p>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0"
                  onClick={() => setEditing(true)}
                >
                  <Edit2 className="w-3 h-3" />
                </Button>
              </div>
            )}
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <Plus className="w-4 h-4 mr-2" />
                New Version
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Copy className="w-4 h-4 mr-2" />
                Duplicate Scene
              </DropdownMenuItem>
              <DropdownMenuItem className="text-red-500">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Scene
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Clips Grid */}
      {expanded && (
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {scene.clips.map((clip, index) => (
              <ClipCard key={clip.id} clip={clip} clipIndex={index} />
            ))}
            
            <button className="border-2 border-dashed border-neutral-700 rounded-lg p-6 hover:border-violet-500 hover:bg-violet-950/10 transition-colors flex flex-col items-center justify-center gap-2 min-h-[200px]">
              <Plus className="w-6 h-6 text-neutral-500" />
              <span className="text-sm text-neutral-500">Add Clip</span>
            </button>
          </div>
        </div>
      )}
    </Card>
  );
}
