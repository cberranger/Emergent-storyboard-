import React from 'react';
import { X, Download, Info } from 'lucide-react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

const MediaViewerDialog = ({ open, onOpenChange, content }) => {
  if (!content) return null;

  const handleDownload = () => {
    if (content.url) {
      const link = document.createElement('a');
      link.href = content.url;
      link.download = `${content.content_type}_${content.id}.${content.content_type === 'image' ? 'png' : 'mp4'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-6xl max-h-[95vh] overflow-hidden p-0">
        <div className="flex h-full">
          {/* Media Display */}
          <div className="flex-1 flex items-center justify-center bg-black relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onOpenChange(false)}
              className="absolute top-4 right-4 z-10 bg-black/50 hover:bg-black/70 text-white"
              data-testid="close-media-viewer-btn"
            >
              <X className="w-4 h-4" />
            </Button>
            
            {content.url ? (
              content.content_type === 'image' ? (
                <img 
                  src={content.url} 
                  alt="Generated content" 
                  className="max-w-full max-h-full object-contain"
                  style={{ maxHeight: '90vh' }}
                />
              ) : (
                <video 
                  src={content.url} 
                  controls
                  className="max-w-full max-h-full object-contain"
                  style={{ maxHeight: '90vh' }}
                />
              )
            ) : (
              <div className="text-center text-secondary">
                <div className="text-6xl mb-4">🎨</div>
                <div>Content is processing...</div>
              </div>
            )}
          </div>

          {/* Info Panel */}
          <div className="w-80 bg-panel-dark border-l border-panel overflow-y-auto">
            <div className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-primary">Generation Info</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownload}
                  disabled={!content.url}
                  className="btn-secondary"
                  data-testid="download-content-btn"
                >
                  <Download className="w-4 h-4" />
                </Button>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="text-xs text-secondary mb-1">Type</div>
                  <Badge variant="outline" className="capitalize">
                    {content.content_type}
                  </Badge>
                </div>

                <div>
                  <div className="text-xs text-secondary mb-1">Status</div>
                  <Badge 
                    variant={content.is_selected ? "default" : "secondary"}
                    className={content.is_selected ? "bg-green-600" : ""}
                  >
                    {content.is_selected ? 'Selected' : 'Available'}
                  </Badge>
                </div>

                <div>
                  <div className="text-xs text-secondary mb-1">Server</div>
                  <div className="text-sm text-primary">{content.server_name}</div>
                </div>

                <div>
                  <div className="text-xs text-secondary mb-1">Model</div>
                  <div className="text-sm text-primary">{content.model_name}</div>
                  {content.model_type && (
                    <Badge variant="outline" className="text-xs mt-1">
                      {content.model_type}
                    </Badge>
                  )}
                </div>

                <div>
                  <div className="text-xs text-secondary mb-1">Prompt</div>
                  <div className="text-sm text-primary p-2 bg-panel rounded border border-panel whitespace-pre-wrap">
                    {content.prompt}
                  </div>
                </div>

                {content.negative_prompt && (
                  <div>
                    <div className="text-xs text-secondary mb-1">Negative Prompt</div>
                    <div className="text-sm text-primary p-2 bg-panel rounded border border-panel whitespace-pre-wrap">
                      {content.negative_prompt}
                    </div>
                  </div>
                )}

                <div>
                  <div className="text-xs text-secondary mb-1">Generation Parameters</div>
                  <Card className="bg-panel border-panel">
                    <CardContent className="p-3">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {Object.entries(content.generation_params || {}).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-secondary capitalize">{key}:</span>
                            <span className="text-primary">{value}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div>
                  <div className="text-xs text-secondary mb-1">Created</div>
                  <div className="text-sm text-primary">
                    {new Date(content.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MediaViewerDialog;