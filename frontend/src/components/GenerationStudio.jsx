import React, { useState, useEffect } from 'react';
import { Wand2, Plus, Eye, Grid, List, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { projectService } from '@/services';
import EnhancedGenerationDialog from './EnhancedGenerationDialog';
import MediaViewerDialog from './MediaViewerDialog';

const GenerationStudio = ({ project, comfyUIServers }) => {
  const [clips, setClips] = useState([]);
  const [scenes, setScenes] = useState([]);
  const [selectedClip, setSelectedClip] = useState(null);
  const [selectedScene, setSelectedScene] = useState(null);
  const [showGenerationDialog, setShowGenerationDialog] = useState(false);
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [sceneFilter, setSceneFilter] = useState('all');

  useEffect(() => {
    if (project?.id) {
      fetchData();
    }
  }, [project]);

  const fetchData = async () => {
    try {
      setLoading(true);

      const [scenesData, clipsData] = await Promise.all([
        projectService.getProjectScenes(project.id),
        projectService.getProjectClips(project.id)
      ]);

      setScenes(scenesData || []);
      setClips(clipsData || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredClips = clips.filter(clip => {
    const matchesSearch = !searchQuery ||
      clip.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      clip.lyrics?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesScene = sceneFilter === 'all' || clip.scene_id === sceneFilter;

    return matchesSearch && matchesScene;
  });

  const handleGenerate = (clip) => {
    setSelectedClip(clip);
    setShowGenerationDialog(true);
  };

  const handleViewContent = (content) => {
    setSelectedContent(content);
    setShowMediaViewer(true);
  };

  const handleGenerationComplete = () => {
    fetchData(); // Refresh data to show new generations
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-secondary">Loading generation studio...</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">Generation Studio</h1>
          <p className="text-sm text-gray-400">AI-powered image and video generation for your storyboard</p>
        </div>
        <Badge variant="outline" className="text-xs">
          {filteredClips.length} clips
        </Badge>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Search clips..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-64 bg-white border-slate-300"
            />
          </div>

          {/* Scene Filter */}
          <Select value={sceneFilter} onValueChange={setSceneFilter}>
            <SelectTrigger className="w-48 bg-white border-slate-300">
              <SelectValue placeholder="Filter by scene" />
            </SelectTrigger>
            <SelectContent className="bg-white border-slate-300">
              <SelectItem value="all">All Scenes</SelectItem>
              {scenes.map(scene => (
                <SelectItem key={scene.id} value={scene.id}>
                  {scene.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* View Mode */}
        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
            className="h-8 px-3"
          >
            <Grid className="w-4 h-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('list')}
            className="h-8 px-3"
          >
            <List className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {filteredClips.length === 0 ? (
          <div className="text-center py-12">
            <Wand2 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-400 mb-2">No clips found</h3>
            <p className="text-gray-500">
              {searchQuery || sceneFilter !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Create some clips in the Timeline to start generating content'
              }
            </p>
          </div>
        ) : (
          <div className={`grid gap-4 ${
            viewMode === 'grid'
              ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
              : 'grid-cols-1'
          }`}>
            {filteredClips.map(clip => {
              const scene = scenes.find(s => s.id === clip.scene_id);

              return (
                <Card key={clip.id} className="bg-white border-slate-200 hover:border-slate-300 transition-colors">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-sm font-medium text-slate-800 truncate">
                          {clip.name}
                        </CardTitle>
                        <p className="text-xs text-gray-400 truncate">
                          Scene: {scene?.name || 'Unknown'}
                        </p>
                      </div>
                      <Badge variant="outline" className="text-xs ml-2">
                        {clip.length}s
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-3">
                    {/* Preview */}
                    <div className="aspect-video bg-slate-100 rounded flex items-center justify-center">
                      {clip.generated_images?.length > 0 ? (
                        <img
                          src={clip.generated_images[0].url}
                          alt="Generated content"
                          className="w-full h-full object-cover rounded cursor-pointer"
                          onClick={() => handleViewContent(clip.generated_images[0])}
                        />
                      ) : clip.generated_videos?.length > 0 ? (
                        <video
                          src={clip.generated_videos[0].url}
                          className="w-full h-full object-cover rounded cursor-pointer"
                          onClick={() => handleViewContent(clip.generated_videos[0])}
                        />
                      ) : (
                        <div className="text-center text-gray-500">
                          <Wand2 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                          <div className="text-xs">No content yet</div>
                        </div>
                      )}
                    </div>

                    {/* Content Count */}
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <span>{(clip.generated_images?.length || 0) + (clip.generated_videos?.length || 0)} items</span>
                      <span>{clip.generated_images?.length || 0} img, {clip.generated_videos?.length || 0} vid</span>
                    </div>

                    {/* Actions */}
                    <div className="flex space-x-2">
                      <Button
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700"
                        size="sm"
                        onClick={() => handleGenerate(clip)}
                      >
                        <Wand2 className="w-4 h-4 mr-2" />
                        Generate
                      </Button>
                      {(clip.generated_images?.length > 0 || clip.generated_videos?.length > 0) && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedClip(clip)}
                          className="px-3"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Generation Dialog */}
      {showGenerationDialog && selectedClip && (
        <EnhancedGenerationDialog
          open={showGenerationDialog}
          onOpenChange={setShowGenerationDialog}
          clip={selectedClip}
          servers={comfyUIServers}
          onGenerated={handleGenerationComplete}
        />
      )}

      {/* Media Viewer */}
      {showMediaViewer && selectedContent && (
        <MediaViewerDialog
          open={showMediaViewer}
          onOpenChange={setShowMediaViewer}
          content={selectedContent}
        />
      )}
    </div>
  );
};

export default GenerationStudio;
