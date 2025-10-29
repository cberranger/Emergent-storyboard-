import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, RefreshCw, Grid, List } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { modelService } from '@/services';
import ModelCard from './ModelCard';

const ModelBrowser = ({ serverId, onModelUpdate }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [serverFilter, setServerFilter] = useState('all');
  const [activeFilter, setActiveFilter] = useState('active'); // New state for active/inactive filter
  const [viewMode, setViewMode] = useState('grid');
  const [syncing, setSyncing] = useState(false);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const params = {};
      if (typeFilter !== 'all') params.type = typeFilter;
      if (serverFilter !== 'all') params.server_source = serverFilter;
      // Filter by active status
      if (activeFilter === 'active') {
        params.is_active = true;
      } else if (activeFilter === 'inactive') {
        params.is_active = false;
      }
      // If 'all', don't set the is_active parameter
      
      const data = await modelService.getModels(params);
      setModels(data);
    } catch (error) {
      console.error('Error fetching models:', error);
    } finally {
      setLoading(false);
    }
  };

  const syncServerModels = async () => {
    if (!serverId) return;
    
    setSyncing(true);
    try {
      const data = await modelService.syncServerModels(serverId);
      toast.success(data.message);
      fetchModels();
    } catch (error) {
      console.error('Error syncing models:', error);
    } finally {
      setSyncing(false);
    }
  };

  const handleModelUpdate = (updatedModel) => {
    setModels(prev => 
      prev.map(model => 
        model.id === updatedModel.id ? updatedModel : model
      )
    );
    onModelUpdate?.(updatedModel);
  };

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === 'all' || model.type === typeFilter;
    const matchesServer = serverFilter === 'all' || model.server_source === serverFilter;
    return matchesSearch && matchesType && matchesServer;
  });

  const getModelTypeStats = () => {
    const stats = { checkpoint: 0, lora: 0, other: 0 };
    models.forEach(model => {
      if (model.type === 'checkpoint') stats.checkpoint++;
      else if (model.type === 'lora') stats.lora++;
      else stats.other++;
    });
    return stats;
  };

  const stats = getModelTypeStats();

  useEffect(() => {
    fetchModels();
  }, [typeFilter, serverFilter, activeFilter]);

  return (
    <div className="space-y-6">
      {/* Header with Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-primary">Model Library</h2>
          <div className="flex space-x-2">
            <Badge variant="secondary">Checkpoints: {stats.checkpoint}</Badge>
            <Badge variant="secondary">LoRAs: {stats.lora}</Badge>
            <Badge variant="secondary">Other: {stats.other}</Badge>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
          >
            {viewMode === 'grid' ? <List className="w-4 h-4" /> : <Grid className="w-4 h-4" />}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchModels}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {serverId && (
            <Button
              variant="outline"
              size="sm"
              onClick={syncServerModels}
              disabled={syncing}
            >
              <Download className={`w-4 h-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
              Sync Server
            </Button>
          )}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary w-4 h-4" />
          <Input
            placeholder="Search models..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Model Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="checkpoint">Checkpoints</SelectItem>
            <SelectItem value="lora">LoRAs</SelectItem>
            <SelectItem value="vae">VAEs</SelectItem>
          </SelectContent>
        </Select>
        
        <Select value={activeFilter} onValueChange={setActiveFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Model Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="active">Active Only</SelectItem>
            <SelectItem value="inactive">Inactive Only</SelectItem>
            <SelectItem value="all">All Models</SelectItem>
          </SelectContent>
        </Select>
        
        <Select value={serverFilter} onValueChange={setServerFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Server Source" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Servers</SelectItem>
            {/* This would be populated with actual server IDs */}
          </SelectContent>
        </Select>
      </div>

      {/* Models Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-secondary" />
          <span className="ml-2 text-secondary">Loading models...</span>
        </div>
      ) : filteredModels.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-secondary mb-4">
            {searchQuery || typeFilter !== 'all' || serverFilter !== 'all' 
              ? 'No models found matching your filters' 
              : 'No models found'}
          </div>
          {serverId && !searchQuery && typeFilter === 'all' && serverFilter === 'all' && (
            <Button onClick={syncServerModels} disabled={syncing}>
              <Download className={`w-4 h-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
              Sync Models from Server
            </Button>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4' 
          : 'space-y-4'
        }>
          {filteredModels.map((model) => (
            <ModelCard
              key={model.id}
              model={model}
              onUpdate={handleModelUpdate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelBrowser;
