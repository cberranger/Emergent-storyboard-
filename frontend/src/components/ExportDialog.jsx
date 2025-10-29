import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { exportService } from '@/services';
import {
  Download,
  FileVideo,
  FileText,
  Film,
  Code,
  Loader2,
  CheckCircle2
} from 'lucide-react';

const ExportDialog = ({ open, onOpenChange, project }) => {
  const [exportingFormat, setExportingFormat] = useState(null);

  const exportFormats = [
    {
      id: 'fcpxml',
      name: 'Final Cut Pro XML',
      description: 'Export timeline for Final Cut Pro X',
      endpoint: '/export/fcpxml',
      icon: Film,
      extension: 'fcpxml',
      color: 'text-purple-400',
      recommended: true
    },
    {
      id: 'edl',
      name: 'Premiere Pro EDL',
      description: 'Export edit decision list for Adobe Premiere Pro',
      endpoint: '/export/edl',
      icon: FileVideo,
      extension: 'edl',
      color: 'text-blue-400'
    },
    {
      id: 'resolve',
      name: 'DaVinci Resolve XML',
      description: 'Export timeline for DaVinci Resolve',
      endpoint: '/export/resolve',
      icon: FileVideo,
      extension: 'xml',
      color: 'text-red-400'
    },
    {
      id: 'json',
      name: 'JSON Format',
      description: 'Export project data as JSON for custom workflows',
      endpoint: '/export/json',
      icon: Code,
      extension: 'json',
      color: 'text-green-400'
    }
  ];

  const handleExport = async (format) => {
    if (!project?.id) {
      toast.error('No project selected');
      return;
    }

    setExportingFormat(format.id);

    try {
      const data = await exportService.exportProject(project.id, format.id);

      const blob = new Blob([JSON.stringify(data)], {
        type: format.id === 'json' ? 'application/json' : 'text/xml'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.name}_export.${format.extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`Successfully exported to ${format.name}`);
    } catch (error) {
      console.error(`Error exporting to ${format.name}:`, error);
      const errorMsg = error.response?.data?.detail || `Failed to export to ${format.name}`;
      toast.error(errorMsg);
    } finally {
      setExportingFormat(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-panel border-panel max-w-3xl">
        <DialogHeader>
          <DialogTitle className="text-primary flex items-center space-x-2">
            <Download className="w-5 h-5" />
            <span>Export Project</span>
          </DialogTitle>
          <DialogDescription className="text-secondary">
            Export your project timeline to various video editing software formats
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Project Info */}
          <div className="p-4 bg-panel-dark rounded-lg border border-panel">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-primary">{project?.name}</div>
                <div className="text-xs text-secondary mt-1">
                  {project?.description || 'No description'}
                </div>
              </div>
              <Badge variant="outline" className="text-xs">
                Ready to export
              </Badge>
            </div>
          </div>

          {/* Export Format Options */}
          <div className="space-y-3">
            <Label className="text-primary">Choose Export Format</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {exportFormats.map((format) => {
                const Icon = format.icon;
                const isExporting = exportingFormat === format.id;

                return (
                  <Card
                    key={format.id}
                    className={`bg-panel-dark border-panel hover:border-indigo-500/50 transition-all cursor-pointer ${
                      isExporting ? 'border-indigo-500' : ''
                    }`}
                    onClick={() => !isExporting && handleExport(format)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <div className={`p-2 rounded-lg bg-panel ${format.color}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <div className="text-sm font-medium text-primary">
                              {format.name}
                            </div>
                            {format.recommended && (
                              <Badge className="bg-indigo-600 text-xs">
                                Recommended
                              </Badge>
                            )}
                          </div>
                          <div className="text-xs text-secondary mt-1">
                            {format.description}
                          </div>
                          <div className="flex items-center mt-3">
                            {isExporting ? (
                              <Button
                                size="sm"
                                disabled
                                className="h-7 text-xs"
                              >
                                <Loader2 className="w-3 h-3 mr-2 animate-spin" />
                                Exporting...
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-7 text-xs"
                              >
                                <Download className="w-3 h-3 mr-2" />
                                Export .{format.extension}
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Export Notes */}
          <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-200 space-y-1">
                <p className="font-medium">Export Notes:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>All clips, scenes, and timeline positions will be preserved</li>
                  <li>Generated media (images/videos) will be referenced by file path</li>
                  <li>Import the exported file into your chosen video editing software</li>
                  <li>JSON format is useful for custom integrations and backups</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t border-panel">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={exportingFormat !== null}
          >
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ExportDialog;
