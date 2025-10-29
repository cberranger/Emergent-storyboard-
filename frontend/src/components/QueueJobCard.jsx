import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  RotateCcw,
  X,
  Trash2,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
  Image,
  Video,
  Download,
  ExternalLink
} from 'lucide-react';
import { TimelineMetadata } from './MetadataItem';
import { formatDistanceToNow } from 'date-fns';

const QueueJobCard = ({ job, onRetry, onCancel, onDelete }) => {
  const [expanded, setExpanded] = useState(false);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'cancelled':
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'processing':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'cancelled':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getJobTypeIcon = (jobType) => {
    if (jobType === 'video' || jobType?.includes('video')) {
      return <Video className="w-4 h-4" />;
    }
    return <Image className="w-4 h-4" />;
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch (error) {
      return 'Invalid date';
    }
  };

  const calculateProgress = () => {
    if (job.status === 'completed') return 100;
    if (job.status === 'failed' || job.status === 'cancelled') return 0;
    if (job.progress) return Math.round(job.progress * 100);
    if (job.status === 'processing') return 50;
    return 0;
  };

  const canRetry = job.status === 'failed' || job.status === 'cancelled';
  const canCancel = job.status === 'pending' || job.status === 'processing';

  return (
    <Card className="bg-panel border-panel hover:border-indigo-500/30 transition-colors">
      <CardContent className="p-4">
        {/* Main Job Info */}
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-3">
            {/* Header Row */}
            <div className="flex items-center space-x-3">
              {getStatusIcon(job.status)}
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-sm font-medium text-primary">
                    {job.job_type || 'Generation Job'}
                  </h3>
                  {getJobTypeIcon(job.job_type)}
                </div>
                <div className="flex items-center space-x-2 mt-1">
                  <Badge variant="outline" className={`text-xs ${getStatusColor(job.status)}`}>
                    {job.status.toUpperCase()}
                  </Badge>
                  {job.server_name && (
                    <span className="text-xs text-secondary">
                      Server: {job.server_name}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            {job.status === 'processing' && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-secondary">Progress</span>
                  <span className="text-primary">{calculateProgress()}%</span>
                </div>
                <Progress value={calculateProgress()} className="h-2" />
              </div>
            )}

            {/* Metadata */}
            <TimelineMetadata
              createdAt={job.created_at}
              completedAt={job.completed_at}
              priority={job.priority}
            />

            {/* Expandable Details */}
            {expanded && (
              <div className="mt-4 p-3 bg-panel-dark rounded-lg space-y-3">
                {/* Job Details */}
                {job.parameters && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-medium text-primary">Parameters</h4>
                    <div className="text-xs text-secondary space-y-1">
                      {job.parameters.prompt && (
                        <div>
                          <span className="text-primary">Prompt:</span> {job.parameters.prompt}
                        </div>
                      )}
                      {job.parameters.model && (
                        <div>
                          <span className="text-primary">Model:</span> {job.parameters.model}
                        </div>
                      )}
                      {job.parameters.width && job.parameters.height && (
                        <div>
                          <span className="text-primary">Size:</span> {job.parameters.width}x{job.parameters.height}
                        </div>
                      )}
                      {job.parameters.steps && (
                        <div>
                          <span className="text-primary">Steps:</span> {job.parameters.steps}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {job.error && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-medium text-red-400">Error</h4>
                    <div className="text-xs text-red-300 bg-red-500/10 p-2 rounded border border-red-500/30">
                      {job.error}
                    </div>
                  </div>
                )}

                {/* Result */}
                {job.result && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-medium text-primary">Result</h4>
                    {job.result.output_path ? (
                      <div className="flex items-center space-x-2">
                        <a
                          href={job.result.output_path}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>View Output</span>
                        </a>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 px-2 text-xs"
                          onClick={() => window.open(job.result.output_path, '_blank')}
                        >
                          <Download className="w-3 h-3 mr-1" />
                          Download
                        </Button>
                      </div>
                    ) : (
                      <div className="text-xs text-secondary">
                        {JSON.stringify(job.result, null, 2)}
                      </div>
                    )}
                  </div>
                )}

                {/* Job ID */}
                <div className="text-xs text-secondary">
                  <span className="text-primary">Job ID:</span> {job.id}
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 ml-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
              className="h-8 w-8 p-0"
            >
              {expanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>

            {canRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onRetry(job.id)}
                className="h-8 px-2 border-panel hover:bg-panel-dark"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            )}

            {canCancel && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onCancel(job.id)}
                className="h-8 px-2 border-panel hover:bg-panel-dark text-yellow-400"
              >
                <X className="w-4 h-4" />
              </Button>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => onDelete(job.id)}
              className="h-8 px-2 border-panel hover:bg-panel-dark text-red-400"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default QueueJobCard;
