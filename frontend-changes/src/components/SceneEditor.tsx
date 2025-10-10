import { useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Plus, Trash2, Copy } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

interface SceneEditorProps {
  scene: any;
}

export function SceneEditor({ scene }: SceneEditorProps) {
  const [description, setDescription] = useState(scene.description);
  const [duration, setDuration] = useState(scene.duration);

  return (
    <div className="space-y-6 py-6">
      {/* Version Selector */}
      <div className="space-y-2">
        <Label>Scene Version</Label>
        <div className="flex gap-2">
          <Select value={scene.currentVersion.toString()}>
            <SelectTrigger className="flex-1 bg-neutral-800 border-neutral-700">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {scene.versions.map((version: any) => (
                <SelectItem key={version.id} value={version.id.toString()}>
                  {version.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon">
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Separator className="bg-neutral-800" />

      {/* Scene Description */}
      <div className="space-y-2">
        <Label>Scene Description</Label>
        <Textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="min-h-[100px] bg-neutral-800 border-neutral-700"
          placeholder="Describe what happens in this scene..."
        />
      </div>

      {/* Duration */}
      <div className="space-y-2">
        <Label>Duration (seconds)</Label>
        <Input
          type="number"
          value={duration}
          onChange={(e) => setDuration(Number(e.target.value))}
          className="bg-neutral-800 border-neutral-700"
          min={1}
        />
      </div>

      <Separator className="bg-neutral-800" />

      {/* Clips List */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Clips ({scene.clips.length})</Label>
          <Button size="sm" variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            Add Clip
          </Button>
        </div>

        <div className="space-y-2">
          {scene.clips.map((clip: any, index: number) => (
            <Card key={clip.id} className="bg-neutral-800 border-neutral-700 p-3">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">Clip {index + 1}</span>
                  <Badge variant="outline" className="text-xs">
                    {clip.duration}s
                  </Badge>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="h-7 w-7">
                    <Copy className="w-3 h-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-red-500">
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <p className="text-xs text-neutral-400 line-clamp-2">{clip.imagePrompt}</p>
            </Card>
          ))}
        </div>
      </div>

      <Separator className="bg-neutral-800" />

      {/* Actions */}
      <div className="flex gap-2">
        <Button className="flex-1 bg-violet-600 hover:bg-violet-700">
          Save Changes
        </Button>
        <Button variant="outline" className="flex-1">
          <Copy className="w-4 h-4 mr-2" />
          Duplicate Scene
        </Button>
      </div>

      <Button variant="destructive" className="w-full">
        <Trash2 className="w-4 h-4 mr-2" />
        Delete Scene
      </Button>
    </div>
  );
}
