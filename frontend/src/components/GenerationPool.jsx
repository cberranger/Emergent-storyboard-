import React, { useState, useEffect } from 'react';
import { Search, Filter, Grid, List, Trash2, Download, Tag, Image as ImageIcon, Video } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { poolService } from '@/services';

const GenerationPool = ({ project }) => {
  const [poolItems, setPoolItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [contentTypeFilter, setContentTypeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [allTags, setAllTags] = useState([]);

  useEffect(() => {
    if (project?.id) {
      fetchPoolItems();
    }
  }, [project]);

  useEffect(() => {
    filterItems();
  }, [poolItems, contentTypeFilter, searchQuery, selectedTags]);

  const fetchPoolItems = async () => {
    try {
      setLoading(true);
      const data = await poolService.getPoolItems(project.id);
      setPoolItems(data);

      const tags = new Set();
      data.forEach(item => {
        item.tags?.forEach(tag => tags.add(tag));
      });
      setAllTags(Array.from(tags).sort());
    } catch (error) {
      console.error('Error fetching pool items:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterItems = () => {
    let filtered = [...poolItems];

    // Filter by content type
    if (contentTypeFilter !== 'all') {
      filtered = filtered.filter(item => item.content_type === contentTypeFilter);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query) ||
        item.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Filter by selected tags
    if (selectedTags.length > 0) {
      filtered = filtered.filter(item =>
        selectedTags.some(tag => item.tags?.includes(tag))
      );
    }

    setFilteredItems(filtered);
  };

  const handleDeleteItem = async (itemId) => {
    if (!confirm('Are you sure you want to delete this pool item?')) return;

    try {
      await poolService.deletePoolItem(itemId);
      toast.success('Pool item deleted');
      fetchPoolItems();
    } catch (error) {
      console.error('Error deleting pool item:', error);
    }
  };

  const handleTagToggle = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handleApplyToClip = (item) => {
    // This will be handled by the parent component or a modal
    toast.info('Select a clip to apply this item to');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-secondary">Loading generation pool...</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-gray-950">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-gray-200">Generation Pool</h2>
          <Badge variant="outline" className="text-xs">
            {filteredItems.length} items
          </Badge>
        </div>

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

      {/* Filters */}
      <div className="px-4 py-3 border-b border-gray-800 bg-gray-950 space-y-3">
        {/* Search and Content Type */}
        <div className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search by name, description, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-gray-900 border-gray-700"
            />
          </div>

          <Select value={contentTypeFilter} onValueChange={setContentTypeFilter}>
            <SelectTrigger className="w-40 bg-gray-900 border-gray-700">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="image">Images</SelectItem>
              <SelectItem value="video">Videos</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <div className="flex items-center space-x-2 flex-wrap">
            <Tag className="w-4 h-4 text-gray-500" />
            {allTags.map(tag => (
              <Badge
                key={tag}
                variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                className="cursor-pointer hover:bg-gray-700 transition-colors text-xs"
                onClick={() => handleTagToggle(tag)}
              >
                {tag}
              </Badge>
            ))}
            {selectedTags.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedTags([])}
                className="h-6 px-2 text-xs"
              >
                Clear
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Items Grid/List */}
      <div className="flex-1 overflow-auto p-4">
        {filteredItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <ImageIcon className="w-16 h-16 mb-4 opacity-50" />
            <p className="text-lg mb-2">No items in pool</p>
            <p className="text-sm">Generated content will appear here</p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filteredItems.map(item => (
              <Card
                key={item.id}
                className="bg-gray-800 border-gray-700 hover:border-gray-600 transition-colors overflow-hidden group"
              >
                {/* Thumbnail */}
                <div className="relative aspect-square bg-gray-900">
                  <img
                    src={item.thumbnail_url || item.media_url}
                    alt={item.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 left-2">
                    <Badge variant="secondary" className="text-xs">
                      {item.content_type === 'image' ? (
                        <ImageIcon className="w-3 h-3 mr-1" />
                      ) : (
                        <Video className="w-3 h-3 mr-1" />
                      )}
                      {item.content_type}
                    </Badge>
                  </div>

                  {/* Hover Actions */}
                  <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleApplyToClip(item)}
                      className="bg-gray-900/80 hover:bg-gray-800"
                    >
                      Apply
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteItem(item.id)}
                      className="bg-gray-900/80 hover:bg-red-900"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Info */}
                <div className="p-3 space-y-2">
                  <h3 className="text-sm font-medium text-gray-200 truncate">
                    {item.name}
                  </h3>
                  {item.description && (
                    <p className="text-xs text-gray-400 line-clamp-2">
                      {item.description}
                    </p>
                  )}
                  {item.tags && item.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {item.tags.slice(0, 3).map(tag => (
                        <Badge key={tag} variant="outline" className="text-[10px] h-5 px-1">
                          {tag}
                        </Badge>
                      ))}
                      {item.tags.length > 3 && (
                        <Badge variant="outline" className="text-[10px] h-5 px-1">
                          +{item.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                  <div className="text-[10px] text-gray-500">
                    {item.source_type}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredItems.map(item => (
              <Card
                key={item.id}
                className="bg-gray-800 border-gray-700 hover:border-gray-600 transition-colors p-3 flex items-center space-x-4"
              >
                {/* Thumbnail */}
                <div className="w-24 h-24 bg-gray-900 rounded flex-shrink-0">
                  <img
                    src={item.thumbnail_url || item.media_url}
                    alt={item.name}
                    className="w-full h-full object-cover rounded"
                  />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-sm font-medium text-gray-200 truncate">
                      {item.name}
                    </h3>
                    <Badge variant="secondary" className="text-xs flex-shrink-0">
                      {item.content_type === 'image' ? (
                        <ImageIcon className="w-3 h-3 mr-1" />
                      ) : (
                        <Video className="w-3 h-3 mr-1" />
                      )}
                      {item.content_type}
                    </Badge>
                  </div>
                  {item.description && (
                    <p className="text-xs text-gray-400 mb-2 line-clamp-2">
                      {item.description}
                    </p>
                  )}
                  {item.tags && item.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {item.tags.map(tag => (
                        <Badge key={tag} variant="outline" className="text-[10px] h-5 px-1">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleApplyToClip(item)}
                    className="h-8 px-3"
                  >
                    Apply
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteItem(item.id)}
                    className="h-8 px-3 hover:bg-red-900"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GenerationPool;
