import React, { useState, useEffect } from 'react';
import { 
  Cpu, HardDrive, ExternalLink, Download, Settings, 
  Clock, CheckCircle, AlertCircle, Plus, Eye, RefreshCw, Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '@/config';
import { 
  InfoRow, 
  StatsCard, 
  ModelVersionCard, 
  SectionHeader, 
  PermissionsGrid,
  SearchResultItem,
  MetadataGrid 
} from './ModelCardComponents';

const ModelCard = ({ model, onUpdate, onSyncCivitai }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);
  const [searching, setSearching] = useState(false);

  // Get background image from Civitai model
  const getBackgroundImage = () => {
    if (model.civitai_info?.images?.length > 0) {
      const firstImage = model.civitai_info.images[0];
      return firstImage.url || firstImage.src;
    }
    return null;
  };

  const backgroundImage = getBackgroundImage();

  const getModelIcon = (type) => {
    switch (type) {
      case 'checkpoint':
        return <Cpu className="w-4 h-4" />;
      case 'lora':
        return <HardDrive className="w-4 h-4" />;
      default:
        return <Cpu className="w-4 h-4" />;
    }
  };

  const getModelTypeColor = (type) => {
    switch (type) {
      case 'checkpoint':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'lora':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const handleSyncCivitai = async () => {
    if (!model.id) return;
    
    setSyncing(true);
    try {
      const response = await axios.post(`${API}/models/${model.id}/sync-civitai`);
      onUpdate?.(response.data);
      
      // Show appropriate success message based on match quality
      const matchQuality = response.data.civitai_match_quality;
      if (matchQuality === 'low_confidence') {
        toast.success('Model synced with low confidence match. Please verify the details.', {
          duration: 5000
        });
      } else {
        toast.success('Model information synced from Civitai');
      }
    } catch (error) {
      console.error('Error syncing Civitai:', error);
      
      if (error.response?.status === 404) {
        toast.error('No matching model found on Civitai. Try searching manually.');
      } else if (error.response?.status === 403) {
        toast.error(error.response.data.detail || 'This model is not active on any backend server.');
      } else if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Failed to sync from Civitai API');
      } else {
        toast.error('Failed to sync from Civitai API');
      }
    } finally {
      setSyncing(false);
    }
  };

  const handleManualSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setSearching(true);
    try {
      const response = await axios.post(`${API}/models/${model.id}/search-civitai`, {
        search_query: searchQuery.trim()
      });
      
      setSearchResults(response.data.matches);
      
      if (response.data.matches.length === 0) {
        toast.error('No results found. Try different keywords.');
      } else {
        toast.success(`Found ${response.data.matches.length} potential matches`);
      }
    } catch (error) {
      console.error('Error searching Civitai:', error);
      if (error.response?.status === 403) {
        toast.error(error.response.data.detail || 'This model is not active on any backend server.');
      } else {
        toast.error('Failed to search Civitai');
      }
    } finally {
      setSearching(false);
    }
  };

  const handleLinkModel = async (civitaiModelId) => {
    try {
      setSearching(true);
      const response = await axios.post(`${API}/models/${model.id}/link-civitai`, {
        civitai_model_id: civitaiModelId
      });
      
      onUpdate?.(response.data);
      setShowSearch(false);
      setSearchResults([]);
      setSearchQuery('');
      toast.success('Model successfully linked to Civitai');
    } catch (error) {
      console.error('Error linking model:', error);
      toast.error('Failed to link model');
    } finally {
      setSearching(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleDateString();
  };

  return (
    <>
      <Card 
        className="glass-panel cursor-pointer hover:shadow-lg transition-all relative overflow-hidden" 
        onClick={() => setShowDetails(true)}
        style={{
          backgroundImage: backgroundImage ? `linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)), url(${backgroundImage})` : 'none',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <CardHeader className="pb-3 relative z-10">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              {getModelIcon(model.type)}
              <CardTitle className="text-primary text-sm font-medium truncate">
                {model.name}
              </CardTitle>
            </div>
            <Badge variant={model.is_active ? "default" : "secondary"} className="text-xs">
              {model.type} {model.is_active ? "✓" : ""}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-0 relative z-10">
          <div className="flex items-center justify-between text-xs text-secondary">
            <span>{model.server_source || 'Unknown'}</span>
            {model.civitai_info ? (
              <div className="flex items-center space-x-1 text-green-400">
                <CheckCircle className="w-3 h-3" />
                <span>Synced</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1 text-yellow-400">
                <AlertCircle className="w-3 h-3" />
                <span>Not Synced</span>
              </div>
            )}
          </div>
          
          {model.configuration_presets && model.configuration_presets.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-secondary mb-1">Presets:</p>
              <div className="flex flex-wrap gap-1">
                {model.configuration_presets.slice(0, 3).map((preset) => (
                  <Badge key={preset.id} variant="outline" className="text-xs">
                    {preset.name}
                  </Badge>
                ))}
                {model.configuration_presets.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{model.configuration_presets.length - 3}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent 
          className="max-w-4xl max-h-[80vh] overflow-y-auto"
          aria-describedby="model-details-description"
        >
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {getModelIcon(model.type)}
              <span>{model.name}</span>
              <Badge className={getModelTypeColor(model.type)}>
                {model.type}
              </Badge>
            </DialogTitle>
            <p id="model-details-description" className="text-sm text-secondary">
              View and manage model details, configuration presets, and Civitai information
            </p>
          </DialogHeader>
          
          <Tabs defaultValue="info" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="info">Information</TabsTrigger>
              <TabsTrigger value="presets">Configuration Presets</TabsTrigger>
              <TabsTrigger value="civitai">Civitai Details</TabsTrigger>
            </TabsList>
            
            <TabsContent value="info" className="space-y-4">
                <div className="space-y-4">
                  <SectionHeader>Basic Information</SectionHeader>
                  <MetadataGrid 
                    metadata={{
                      "Type": model.type || 'N/A',
                      "Filename": model.filename || 'N/A',
                      "Server Source": model.server_source || 'N/A',
                      "Created": model.created_at ? new Date(model.created_at).toLocaleDateString() : 'N/A',
                      "Last Synced": model.last_synced_at ? new Date(model.last_synced_at).toLocaleDateString() : 'Never'
                    }}
                  />
                  
                  <SectionHeader>Status</SectionHeader>
                  <div className="flex items-center space-x-2">
                    {model.is_available ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm">Available</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-4 h-4 text-red-500" />
                        <span className="text-sm">Not Available</span>
                      </>
                    )}
                    <Badge variant={model.is_available ? "default" : "destructive"} className="ml-2">
                      {model.is_available ? "Ready" : "Unavailable"}
                    </Badge>
                  </div>
                  
                  {model.metadata && Object.keys(model.metadata).length > 0 && (
                    <>
                      <SectionHeader>Additional Metadata</SectionHeader>
                      <div className="text-sm text-secondary">
                        {Object.entries(model.metadata).map(([key, value]) => (
                          <div key={key} className="mb-1">
                            <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
            </TabsContent>
            
            <TabsContent value="presets" className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-primary">Configuration Presets</h4>
                <Button size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Preset
                </Button>
              </div>
              
              {model.configuration_presets && model.configuration_presets.length > 0 ? (
                <div className="grid gap-3">
                  {model.configuration_presets.map((preset) => (
                    <Card key={preset.id} className="bg-panel-dark">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm">{preset.name}</CardTitle>
                          <div className="flex space-x-2">
                            <Button size="sm" variant="ghost">
                              <Settings className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                        {preset.description && (
                          <p className="text-xs text-secondary">{preset.description}</p>
                        )}
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="grid grid-cols-3 gap-4 text-xs">
                          <div>
                            <span className="text-secondary">CFG Scale:</span>
                            <span className="ml-2">{preset.cfg_scale}</span>
                          </div>
                          <div>
                            <span className="text-secondary">Steps:</span>
                            <span className="ml-2">{preset.steps}</span>
                          </div>
                          <div>
                            <span className="text-secondary">Sampler:</span>
                            <span className="ml-2">{preset.sampler}</span>
                          </div>
                          <div>
                            <span className="text-secondary">Resolution:</span>
                            <span className="ml-2">{preset.resolution_width}x{preset.resolution_height}</span>
                          </div>
                          <div>
                            <span className="text-secondary">Batch Size:</span>
                            <span className="ml-2">{preset.batch_size}</span>
                          </div>
                          <div>
                            <span className="text-secondary">Seed:</span>
                            <span className="ml-2">{preset.seed === -1 ? 'Random' : preset.seed}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-secondary">
                  <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No configuration presets found</p>
                  <p className="text-sm">Create presets to save commonly used generation settings</p>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="civitai" className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-primary">Civitai Information</h4>
                <div className="flex space-x-2">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={() => setShowSearch(true)}
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Manual Search
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={handleSyncCivitai}
                    disabled={syncing}
                  >
                    {syncing ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Syncing...
                      </>
                    ) : model.civitai_info ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Resync
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4 mr-2" />
                        Sync from Civitai
                      </>
                    )}
                  </Button>
                </div>
              </div>
              
              {model.civitai_info ? (
                <div className="space-y-4">
                  {/* Match Quality Indicator */}
                  {model.civitai_match_quality === 'low_confidence' && (
                    <div className="bg-yellow-500/20 border border-yellow-500/30 rounded p-3">
                      <div className="flex items-center space-x-2 text-yellow-400">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Low Confidence Match</span>
                      </div>
                      <p className="text-xs text-yellow-300 mt-1">
                        Please verify the model details are correct
                      </p>
                    </div>
                  )}
                  
                  {/* Model Header with Image */}
                  <div className="relative rounded-lg overflow-hidden">
                    {model.civitai_info.images?.length > 0 && (
                      <img 
                        src={model.civitai_info.images[0].url || model.civitai_info.images[0].src}
                        alt={model.civitai_info.name}
                        className="w-full h-48 object-cover"
                      />
                    )}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                      <h3 className="text-lg font-bold text-white">
                        {model.civitai_info.name}
                      </h3>
                      <p className="text-sm text-gray-300">
                        Model ID: {model.civitai_info.modelId}
                      </p>
                    </div>
                  </div>

                  {/* Basic Info */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-secondary">Type:</span>
                      <span className="ml-2">{model.civitai_info.type || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-secondary">Base Model:</span>
                      <span className="ml-2">{model.civitai_info.modelVersions?.[0]?.baseModel || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-secondary">NSFW Level:</span>
                      <span className="ml-2">{model.civitai_info.nsfwLevel || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-secondary">SFW Only:</span>
                      <span className="ml-2">{model.civitai_info.sfwOnly ? 'Yes' : 'No'}</span>
                    </div>
                  </div>

                  {/* Stats */}
                  {model.civitai_info.stats && (
                    <StatsCard 
                      title="Statistics"
                      stats={{
                        "Downloads": model.civitai_info.stats.downloadCount?.toLocaleString() || 'N/A',
                        "Thumbs Up": model.civitai_info.stats.thumbsUpCount?.toLocaleString() || 'N/A',
                        "Favorites": model.civitai_info.stats.favoriteCount?.toLocaleString() || 'N/A',
                        "Rating": model.civitai_info.stats.rating || 'N/A'
                      }}
                    />
                  )}

                  {/* Description */}
                  {model.civitai_info.description && (
                    <div>
                      <SectionHeader>Description</SectionHeader>
                      <div 
                        className="text-sm text-secondary max-h-32 overflow-y-auto"
                        dangerouslySetInnerHTML={{ 
                          __html: model.civitai_info.description.length > 300 
                            ? model.civitai_info.description.substring(0, 300) + '...' 
                            : model.civitai_info.description 
                        }} 
                      />
                    </div>
                  )}

                  {/* Tags */}
                  {model.civitai_info.tags && model.civitai_info.tags.length > 0 && (
                    <div>
                      <SectionHeader>Tags</SectionHeader>
                      <div className="flex flex-wrap gap-1">
                        {model.civitai_info.tags.slice(0, 10).map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {model.civitai_info.tags.length > 10 && (
                          <Badge variant="outline" className="text-xs">
                            +{model.civitai_info.tags.length - 10}
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Model Versions */}
                  {model.civitai_info.modelVersions && model.civitai_info.modelVersions.length > 0 && (
                    <div>
                      <SectionHeader>Model Versions</SectionHeader>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {model.civitai_info.modelVersions.slice(0, 3).map((version, index) => (
                          <ModelVersionCard key={index} version={version} />
                        ))}
                        {model.civitai_info.modelVersions.length > 3 && (
                          <p className="text-xs text-secondary">
                            +{model.civitai_info.modelVersions.length - 3} more versions
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Permissions */}
                  <PermissionsGrid 
                    permissions={{
                      "Derivatives": model.civitai_info.allowDerivatives ? 'Allowed' : 'Not Allowed',
                      "No Credit": model.civitai_info.allowNoCredit ? 'Allowed' : 'Credit Required',
                      "Commercial": model.civitai_info.allowCommercialUse?.length > 0 ? 'Allowed' : 'Not Allowed',
                      "Availability": model.civitai_info.availability || 'N/A'
                    }}
                  />
                </div>
              ) : (
                <div className="text-center py-8 text-secondary">
                  <Download className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No Civitai data available</p>
                  <p className="text-sm">Click "Sync from Civitai" to fetch model information</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      {/* Manual Search Dialog */}
      <Dialog open={showSearch} onOpenChange={setShowSearch}>
        <DialogContent 
          className="max-w-3xl max-h-[80vh] overflow-y-auto"
          aria-describedby="search-dialog-description"
        >
          <DialogHeader>
            <DialogTitle>Search Civitai Manually</DialogTitle>
            <p id="search-dialog-description" className="text-sm text-secondary">
              Search for Civitai models to link with this model
            </p>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                placeholder="Enter search terms (e.g., RealVisXL V5 Lightning)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleManualSearch()}
              />
              <Button 
                onClick={handleManualSearch}
                disabled={searching}
              >
                {searching ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
            </div>
            
            {searchResults.length > 0 && (
              <div className="space-y-3">
                <SectionHeader>Search Results</SectionHeader>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {searchResults.map((result, index) => (
                    <SearchResultItem 
                      key={index} 
                      result={result} 
                      onSelect={(model) => handleLinkModel(model)} 
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ModelCard;
