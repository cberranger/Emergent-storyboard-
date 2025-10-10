import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/config';
import { toast } from 'sonner';
import { Palette, Plus, Edit, Trash2, Copy, TrendingUp, Filter, Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const CATEGORIES = [
  { value: 'custom', label: 'Custom' },
  { value: 'cinematic', label: 'Cinematic' },
  { value: 'anime', label: 'Anime' },
  { value: 'realistic', label: 'Realistic' },
  { value: 'artistic', label: 'Artistic' },
  { value: 'abstract', label: 'Abstract' },
];

const StyleTemplateLibrary = ({ activeProject }) => {
  const [templates, setTemplates] = useState([]);
  const [filteredTemplates, setFilteredTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'custom',
    model: '',
    negative_prompt: '',
    loras: [],
    params: {}
  });

  // Separate state for LoRA input
  const [loraInput, setLoraInput] = useState({ name: '', weight: 1.0 });

  // Separate state for params input
  const [paramsJson, setParamsJson] = useState('{}');

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    filterTemplates();
  }, [templates, searchQuery, categoryFilter]);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/style-templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
      toast.error('Failed to load style templates');
    } finally {
      setLoading(false);
    }
  };

  const filterTemplates = () => {
    let filtered = [...templates];

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(query) ||
        (t.description && t.description.toLowerCase().includes(query))
      );
    }

    // Filter by category
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(t => t.category === categoryFilter);
    }

    setFilteredTemplates(filtered);
  };

  const handleCreateTemplate = () => {
    setIsEditing(false);
    setFormData({
      name: '',
      description: '',
      category: 'custom',
      model: '',
      negative_prompt: '',
      loras: [],
      params: {}
    });
    setParamsJson('{}');
    setLoraInput({ name: '', weight: 1.0 });
    setIsDialogOpen(true);
  };

  const handleEditTemplate = (template) => {
    setIsEditing(true);
    setSelectedTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      category: template.category || 'custom',
      model: template.model || '',
      negative_prompt: template.negative_prompt || '',
      loras: template.loras || [],
      params: template.params || {}
    });
    setParamsJson(JSON.stringify(template.params || {}, null, 2));
    setLoraInput({ name: '', weight: 1.0 });
    setIsDialogOpen(true);
  };

  const handleSaveTemplate = async () => {
    if (!formData.name.trim()) {
      toast.error('Template name is required');
      return;
    }

    try {
      // Parse params JSON
      let params = {};
      try {
        params = JSON.parse(paramsJson);
      } catch (e) {
        toast.error('Invalid JSON in parameters');
        return;
      }

      const templateData = {
        ...formData,
        params,
        is_public: false
      };

      if (isEditing && selectedTemplate) {
        await axios.put(`${API}/style-templates/${selectedTemplate.id}`, templateData);
        toast.success('Template updated successfully');
      } else {
        await axios.post(`${API}/style-templates`, templateData);
        toast.success('Template created successfully');
      }

      setIsDialogOpen(false);
      fetchTemplates();
    } catch (error) {
      console.error('Error saving template:', error);
      toast.error(`Failed to ${isEditing ? 'update' : 'create'} template`);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      await axios.delete(`${API}/style-templates/${templateId}`);
      toast.success('Template deleted successfully');
      fetchTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);
      toast.error('Failed to delete template');
    }
  };

  const handleUseTemplate = async (template) => {
    try {
      await axios.post(`${API}/style-templates/${template.id}/use`);
      toast.success(`Applied template: ${template.name}`);
      fetchTemplates(); // Refresh to update use count
    } catch (error) {
      console.error('Error using template:', error);
      toast.error('Failed to apply template');
    }
  };

  const handleDuplicateTemplate = (template) => {
    setIsEditing(false);
    setSelectedTemplate(null);
    setFormData({
      name: `${template.name} (Copy)`,
      description: template.description || '',
      category: template.category || 'custom',
      model: template.model || '',
      negative_prompt: template.negative_prompt || '',
      loras: template.loras || [],
      params: template.params || {}
    });
    setParamsJson(JSON.stringify(template.params || {}, null, 2));
    setLoraInput({ name: '', weight: 1.0 });
    setIsDialogOpen(true);
  };

  const handleAddLora = () => {
    if (!loraInput.name.trim()) {
      toast.error('LoRA name is required');
      return;
    }

    setFormData({
      ...formData,
      loras: [...formData.loras, { name: loraInput.name, weight: loraInput.weight }]
    });
    setLoraInput({ name: '', weight: 1.0 });
  };

  const handleRemoveLora = (index) => {
    setFormData({
      ...formData,
      loras: formData.loras.filter((_, i) => i !== index)
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      custom: 'bg-gray-500',
      cinematic: 'bg-purple-500',
      anime: 'bg-pink-500',
      realistic: 'bg-blue-500',
      artistic: 'bg-orange-500',
      abstract: 'bg-green-500'
    };
    return colors[category] || 'bg-gray-500';
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="border-b border-panel p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-primary flex items-center gap-2">
              <Palette className="w-6 h-6" />
              Style Template Library
            </h2>
            <p className="text-sm text-secondary mt-1">
              Save and reuse generation styles for consistent results
            </p>
          </div>
          <Button onClick={handleCreateTemplate} className="gap-2">
            <Plus className="w-4 h-4" />
            New Template
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
            <Input
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {CATEGORIES.map(cat => (
                <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-secondary">Loading templates...</div>
          </div>
        ) : filteredTemplates.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <Palette className="w-16 h-16 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-primary mb-2">
                {templates.length === 0 ? 'No Templates Yet' : 'No Matching Templates'}
              </h3>
              <p className="text-sm text-secondary mb-4">
                {templates.length === 0
                  ? 'Create style templates to save your favorite generation settings and reuse them across projects.'
                  : 'Try adjusting your search or filter criteria.'}
              </p>
              {templates.length === 0 && (
                <Button onClick={handleCreateTemplate} className="gap-2">
                  <Plus className="w-4 h-4" />
                  Create First Template
                </Button>
              )}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <CardTitle className="text-lg truncate">{template.name}</CardTitle>
                        <Badge className={`${getCategoryColor(template.category)} text-white text-xs`}>
                          {template.category}
                        </Badge>
                      </div>
                      <CardDescription className="line-clamp-2">
                        {template.description || 'No description'}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {/* Model */}
                  {template.model && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">Model</Label>
                      <Badge variant="secondary" className="text-xs">{template.model}</Badge>
                    </div>
                  )}

                  {/* LoRAs */}
                  {template.loras && template.loras.length > 0 && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">LoRAs ({template.loras.length})</Label>
                      <div className="flex flex-wrap gap-1">
                        {template.loras.slice(0, 2).map((lora, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {lora.name} ({lora.weight})
                          </Badge>
                        ))}
                        {template.loras.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{template.loras.length - 2} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Parameters */}
                  {template.params && Object.keys(template.params).length > 0 && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">
                        Parameters ({Object.keys(template.params).length})
                      </Label>
                      <div className="text-xs text-secondary">
                        {Object.keys(template.params).slice(0, 3).join(', ')}
                        {Object.keys(template.params).length > 3 && '...'}
                      </div>
                    </div>
                  )}

                  {/* Use Count */}
                  <div className="flex items-center gap-2 text-xs text-secondary pt-2 border-t border-panel">
                    <TrendingUp className="w-3 h-3" />
                    <span>Used {template.use_count || 0} times</span>
                  </div>
                </CardContent>

                <CardFooter className="flex gap-2 pt-3">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 gap-1"
                    onClick={() => handleUseTemplate(template)}
                  >
                    <Copy className="w-3 h-3" />
                    Apply
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleEditTemplate(template)}
                    className="px-2"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDuplicateTemplate(template)}
                    className="px-2"
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteTemplate(template.id)}
                    className="px-2 text-red-500 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isEditing ? 'Edit Template' : 'Create New Template'}
            </DialogTitle>
            <DialogDescription>
              Save your generation settings for easy reuse
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Template Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Cinematic Portrait Style"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe this style template..."
                rows={2}
              />
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select value={formData.category} onValueChange={(val) => setFormData({ ...formData, category: val })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Model */}
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Input
                id="model"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                placeholder="e.g., flux_dev, sdxl_turbo"
              />
            </div>

            {/* Negative Prompt */}
            <div className="space-y-2">
              <Label htmlFor="neg_prompt">Negative Prompt</Label>
              <Textarea
                id="neg_prompt"
                value={formData.negative_prompt}
                onChange={(e) => setFormData({ ...formData, negative_prompt: e.target.value })}
                placeholder="Things to avoid in generation..."
                rows={2}
              />
            </div>

            {/* LoRAs */}
            <div className="space-y-2">
              <Label>LoRAs</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="LoRA name"
                  value={loraInput.name}
                  onChange={(e) => setLoraInput({ ...loraInput, name: e.target.value })}
                  className="flex-1"
                />
                <Input
                  type="number"
                  placeholder="Weight"
                  value={loraInput.weight}
                  onChange={(e) => setLoraInput({ ...loraInput, weight: parseFloat(e.target.value) || 1.0 })}
                  step="0.1"
                  min="0"
                  max="2"
                  className="w-24"
                />
                <Button onClick={handleAddLora} size="sm">Add</Button>
              </div>

              {formData.loras.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.loras.map((lora, idx) => (
                    <Badge key={idx} variant="secondary" className="gap-1">
                      {lora.name} ({lora.weight})
                      <X
                        className="w-3 h-3 cursor-pointer hover:text-red-500"
                        onClick={() => handleRemoveLora(idx)}
                      />
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Parameters (JSON) */}
            <div className="space-y-2">
              <Label htmlFor="params">Parameters (JSON)</Label>
              <Textarea
                id="params"
                value={paramsJson}
                onChange={(e) => setParamsJson(e.target.value)}
                placeholder='{"steps": 28, "cfg": 3.5, "width": 1024, "height": 1024}'
                rows={4}
                className="font-mono text-xs"
              />
              <p className="text-xs text-secondary">
                Enter generation parameters as JSON (steps, cfg, width, height, etc.)
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveTemplate}>
              {isEditing ? 'Update' : 'Create'} Template
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default StyleTemplateLibrary;
