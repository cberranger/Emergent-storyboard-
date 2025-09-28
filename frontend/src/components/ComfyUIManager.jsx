import React, { useState, useEffect } from 'react';
import { Plus, Server, Wifi, WifiOff, RefreshCw, Monitor, Cpu, HardDrive } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ComfyUIManager = ({ servers, onAddServer, onRefresh }) => {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newServer, setNewServer] = useState({ name: '', url: '', server_type: 'standard', api_key: '' });
  const [serverInfos, setServerInfos] = useState({});
  const [loading, setLoading] = useState({});

  const handleAddServer = async (e) => {
    e.preventDefault();
    if (!newServer.name.trim() || !newServer.url.trim()) return;
    
    // Auto-detect RunPod
    const isRunPod = newServer.url.includes('runpod.ai');
    const serverData = {
      name: newServer.name,
      url: newServer.url,
      server_type: isRunPod ? 'runpod' : 'standard',
      api_key: isRunPod ? newServer.api_key : null
    };
    
    try {
      const response = await axios.post(`${API}/comfyui/servers`, serverData);
      onAddServer && await onAddServer(); // Refresh the list
      setNewServer({ name: '', url: '', server_type: 'standard', api_key: '' });
      setIsAddOpen(false);
      // Fetch info for the new server
      fetchServerInfo(response.data.id);
    } catch (error) {
      console.error('Error adding server:', error);
      toast.error('Failed to add server');
    }
  };

  const fetchServerInfo = async (serverId) => {
    setLoading(prev => ({ ...prev, [serverId]: true }));
    try {
      const response = await axios.get(`${API}/comfyui/servers/${serverId}/info`);
      setServerInfos(prev => ({ ...prev, [serverId]: response.data }));
    } catch (error) {
      console.error('Error fetching server info:', error);
      toast.error('Failed to fetch server info');
    } finally {
      setLoading(prev => ({ ...prev, [serverId]: false }));
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
              <h1 className="text-3xl font-bold text-primary mb-2">ComfyUI Servers</h1>
              <p className="text-secondary">Manage your AI generation servers</p>
            </div>
            
            <div className="flex space-x-3">
              <Button 
                onClick={onRefresh} 
                variant="outline" 
                className="btn-secondary"
                data-testid="refresh-servers-btn"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              
              <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
                <DialogTrigger asChild>
                  <Button className="btn-primary" data-testid="add-server-btn">
                    <Plus className="w-5 h-5 mr-2" />
                    Add Server
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-panel border-panel">
                  <DialogHeader>
                    <DialogTitle className="text-primary">Add ComfyUI Server</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleAddServer} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary mb-2">
                        Server Name
                      </label>
                      <Input
                        className="form-input"
                        placeholder="e.g., Local ComfyUI, RunPod Instance"
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
                          data-testid="server-api-key-input"
                        />
                        <p className="text-xs text-secondary mt-1">
                          Required for RunPod serverless endpoints
                        </p>
                      </div>
                    )}
                    <div className="flex justify-end space-x-3 pt-4">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setIsAddOpen(false)}
                        className="btn-secondary"
                        data-testid="cancel-server-btn"
                      >
                        Cancel
                      </Button>
                      <Button 
                        type="submit" 
                        className="btn-primary"
                        data-testid="submit-server-btn"
                      >
                        Add Server
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Servers Grid */}
          {servers.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-panel-dark flex items-center justify-center">
                <Server className="w-12 h-12 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold text-primary mb-2">No servers configured</h3>
              <p className="text-secondary mb-6">Add your ComfyUI server to start generating content</p>
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
                        
                        <div className="mt-4 pt-3 border-t border-panel">
                          <Button 
                            onClick={() => fetchServerInfo(server.id)} 
                            variant="outline" 
                            size="sm" 
                            className="btn-secondary w-full"
                            disabled={loading[server.id]}
                            data-testid={`refresh-server-${index}-btn`}
                          >
                            <RefreshCw className={`w-4 h-4 mr-2 ${loading[server.id] ? 'animate-spin' : ''}`} />
                            Refresh Info
                          </Button>
                        </div>
                      </CardContent>
                    )}
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComfyUIManager;