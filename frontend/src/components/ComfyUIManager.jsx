import React, { useState, useEffect } from 'react';
import { Plus, Server, Wifi, WifiOff, RefreshCw, Monitor, Cpu, HardDrive, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { comfyuiService } from '@/services';
import { validateURL, sanitizeInput } from '@/utils/validators';
import ModelBrowser from './ModelBrowser';

const ComfyUIManager = ({ servers, onAddServer, onRefresh, onDeleteServer }) => {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newServer, setNewServer] = useState({ name: '', url: '', server_type: 'standard', api_key: '' });
  const [serverInfos, setServerInfos] = useState({});
  const [loading, setLoading] = useState({});

  const handleAddServer = async (e) => {
    e.preventDefault();

    // Validate and sanitize inputs
    const name = sanitizeInput(newServer.name.trim());
    const url = newServer.url.trim();

    if (!name || !url) {
      toast.error('Server name and URL are required');
      return;
    }

    // Validate URL format
    try {
      validateURL(url);
    } catch (error) {
      toast.error(error.message);
      return;
    }

    // Auto-detect RunPod
    const isRunPod = url.includes('runpod.ai');
    const serverData = {
      name,
      url,
      server_type: isRunPod ? 'runpod' : 'standard',
      api_key: isRunPod ? sanitizeInput(newServer.api_key) : null
    };
    
    try {
      const data = await comfyuiService.createServer(serverData);
      onAddServer && await onAddServer();
      setNewServer({ name: '', url: '', server_type: 'standard', api_key: '' });
      setIsAddOpen(false);
      fetchServerInfo(data.id);
    } catch (error) {
      console.error('Error adding server:', error);
    }
  };

  const fetchServerInfo = async (serverId) => {
    setLoading(prev => ({ ...prev, [serverId]: true }));
    try {
      const data = await comfyuiService.getServerInfo(serverId);
      setServerInfos(prev => ({ ...prev, [serverId]: data }));
    } catch (error) {
      console.error('Error fetching server info:', error);
    } finally {
      setLoading(prev => ({ ...prev, [serverId]: false }));
    }
  };

  const handleDeleteServer = async (serverId, serverName) => {
    if (!window.confirm(`Are you sure you want to delete the server "${serverName}"?`)) {
      return;
    }
    
    try {
      await comfyuiService.deleteServer(serverId);
      toast.success('Server deleted successfully');
      setServerInfos(prev => {
        const newInfos = { ...prev };
        delete newInfos[serverId];
        return newInfos;
      });
      onDeleteServer && await onDeleteServer();
    } catch (error) {
      console.error('Error deleting server:', error);
      toast.error('Failed to delete server');
    }
  };

  const fetchAllServerInfos = async () => {
    for (const server of servers) {
      await fetchServerInfo(server.id);
    }
  };

  useEffect(() => {
    if (servers.length > 0) {
      fetchAllServerInfos();
    }
  }, [servers]);

  const getServerStatus = (serverId) => {
    const info = serverInfos[serverId];
    if (loading[serverId]) return 'loading';
    if (!info) return 'unknown';
    return info.is_online ? 'online' : 'offline';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return <Wifi className="w-4 h-4 status-online" />;
      case 'offline': return <WifiOff className="w-4 h-4 status-offline" />;
      case 'loading': return <RefreshCw className="w-4 h-4 status-loading animate-spin" />;
      default: return <Monitor className="w-4 h-4 text-secondary" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'online': return 'Online';
      case 'offline': return 'Offline';
      case 'loading': return 'Checking...';
      default: return 'Unknown';
    }
  };

  return (
    <div className="h-full overflow-auto">
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-primary mb-2">ComfyUI Management</h1>
              <p className="text-secondary">Manage your AI generation servers and model library</p>
            </div>
            
            <div className="flex space-x-3">
              <Button 
                onClick={onRefresh} 
                variant="outline" 
                className="btn-secondary"
              >
                <RefreshCw className="w-5 h-5 mr-2" />
                Refresh
              </Button>
              <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
                <DialogTrigger asChild>
                  <Button 
                    className="btn-primary"
                    data-testid="add-server-btn"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Add Server
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>Add ComfyUI Server</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleAddServer} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary mb-2">
                        Server Name
                      </label>
                      <Input
                        className="form-input"
                        placeholder="My ComfyUI Server"
                        value={newServer.name}
                        onChange={(e) => setNewServer({ ...newServer, name: e.target.value })}
                        required
                        data-testid="server-name-input"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary mb-2">
                        Server URL
                      </label>
                      <Input
                        className="form-input"
                        placeholder="http://localhost:8188 or https://api.runpod.ai/v2/your-endpoint"
                        value={newServer.url}
                        onChange={(e) => setNewServer({ ...newServer, url: e.target.value })}
                        required
                        data-testid="server-url-input"
                      />
                      <p className="text-xs text-secondary mt-1">
                        For RunPod: https://api.runpod.ai/v2/your-endpoint-id
                      </p>
                    </div>
                    
                    {newServer.url.includes('runpod.ai') && (
                      <div>
                        <label className="block text-sm font-medium text-secondary mb-2">
                          RunPod API Key
                        </label>
                        <Input
                          type="password"
                          className="form-input"
                          placeholder="Your RunPod API key"
                          value={newServer.api_key}
                          onChange={(e) => setNewServer({ ...newServer, api_key: e.target.value })}
                          required
                        />
                        <p className="text-xs text-secondary mt-1">
                          Required for RunPod serverless endpoints
                        </p>
                      </div>
                    )}
                    
                    <div className="flex justify-end space-x-2 pt-4">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setIsAddOpen(false)}
                      >
                        Cancel
                      </Button>
                      <Button 
                        type="submit" 
                        className="btn-primary"
                        data-testid="add-server-submit"
                      >
                        Add Server
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="servers" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-panel-dark">
              <TabsTrigger value="servers" className="data-[state=active]:bg-indigo-600">
                Servers ({servers.length})
              </TabsTrigger>
              <TabsTrigger value="models" className="data-[state=active]:bg-indigo-600">
                Model Library
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="servers" className="mt-6">
              {servers.length === 0 ? (
                <div className="text-center py-12">
                  <Server className="w-16 h-16 mx-auto text-secondary mb-4" />
                  <h3 className="text-xl font-semibold text-primary mb-2">No Servers Added</h3>
                  <p className="text-secondary mb-6">Add your first ComfyUI server to get started</p>
                  <Button 
                    onClick={() => setIsAddOpen(true)}
                    className="btn-primary"
                    data-testid="empty-add-server-btn"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Add Server
                  </Button>
                </div>
              ) : (
                <div className="grid-responsive animate-fade-in">
                  {servers.map((server, index) => {
                    const status = getServerStatus(server.id);
                    const info = serverInfos[server.id];
                    
                    return (
                      <Card 
                        key={server.id} 
                        className="glass-panel"
                        data-testid={`server-card-${index}`}
                      >
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <CardTitle className="text-primary flex items-center">
                                {server.name}
                                <div className="ml-2 flex items-center">
                                  {getStatusIcon(status)}
                                </div>
                              </CardTitle>
                              <p className="text-sm text-secondary mt-1">{server.url}</p>
                            </div>
                            <Badge 
                              variant={status === 'online' ? 'default' : 'secondary'}
                              className={
                                status === 'online' 
                                  ? 'bg-green-500/20 text-green-400 border-green-500/30'
                                  : status === 'offline'
                                  ? 'bg-red-500/20 text-red-400 border-red-500/30'
                                  : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                              }
                            >
                              {getStatusText(status)}
                            </Badge>
                          </div>
                        </CardHeader>
                        
                        {info && info.is_online && (
                          <CardContent className="pt-0">
                            <Tabs defaultValue="models" className="w-full">
                              <TabsList className="grid w-full grid-cols-2 bg-panel-dark">
                                <TabsTrigger value="models" className="data-[state=active]:bg-indigo-600">
                                  Models ({info.models.length})
                                </TabsTrigger>
                                <TabsTrigger value="loras" className="data-[state=active]:bg-indigo-600">
                                  LoRAs ({info.loras.length})
                                </TabsTrigger>
                              </TabsList>
                              
                              <TabsContent value="models" className="mt-4">
                                {info.models.length > 0 ? (
                                  <div className="space-y-2 max-h-32 overflow-y-auto">
                                    {info.models.slice(0, 5).map((model, idx) => (
                                      <div key={idx} className="flex items-center text-sm">
                                        <Cpu className="w-3 h-3 text-secondary mr-2 flex-shrink-0" />
                                        <span className="text-primary truncate">{model.name}</span>
                                      </div>
                                    ))}
                                    {info.models.length > 5 && (
                                      <div className="text-xs text-secondary">
                                        +{info.models.length - 5} more models
                                      </div>
                                    )}
                                  </div>
                                ) : (
                                  <div className="text-sm text-secondary">No models found</div>
                                )}
                              </TabsContent>
                              
                              <TabsContent value="loras" className="mt-4">
                                {info.loras.length > 0 ? (
                                  <div className="space-y-2 max-h-32 overflow-y-auto">
                                    {info.loras.slice(0, 5).map((lora, idx) => (
                                      <div key={idx} className="flex items-center text-sm">
                                        <HardDrive className="w-3 h-3 text-secondary mr-2 flex-shrink-0" />
                                        <span className="text-primary truncate">{lora.name}</span>
                                      </div>
                                    ))}
                                    {info.loras.length > 5 && (
                                      <div className="text-xs text-secondary">
                                        +{info.loras.length - 5} more LoRAs
                                      </div>
                                    )}
                                  </div>
                                ) : (
                                  <div className="text-sm text-secondary">No LoRAs found</div>
                                )}
                              </TabsContent>
                            </Tabs>
                          </CardContent>
                        )}
                        
                        <CardContent className="pt-0">
                          <div className="flex items-center justify-between mt-4">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => onRefresh(server.id)}
                              disabled={loading[server.id]}
                              className="text-xs"
                            >
                              <RefreshCw className={`w-3 h-3 mr-1 ${loading[server.id] ? 'animate-spin' : ''}`} />
                              Refresh
                            </Button>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteServer(server.id, server.name)}
                              className="text-xs"
                            >
                              <Trash2 className="w-3 h-3 mr-1" />
                              Delete
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="models" className="mt-6">
              <ModelBrowser 
                serverId={servers.length > 0 ? servers[0].id : null}
                onModelUpdate={(model) => {
                  console.log('Model updated:', model);
                }}
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default ComfyUIManager;