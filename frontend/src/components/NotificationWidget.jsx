import React from 'react';
import { Bell, ChevronDown, ChevronUp, X, Loader2, CheckCircle2, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card } from '@/components/ui/card';
import { useNotifications } from '@/contexts/NotificationContext';

const NotificationWidget = () => {
  const {
    activeJobs,
    completedJobs,
    isExpanded,
    setIsExpanded,
    dismissJob,
    dismissAll
  } = useNotifications();

  const totalJobs = activeJobs.length + completedJobs.length;

  if (totalJobs === 0) {
    return null;
  }

  const renderJobItem = (job, isActive) => {
    const thumbnailUrl = job.result?.thumbnail_url || job.result?.url;
    const progress = job.progress || 0;

    return (
      <div
        key={job.id}
        className="flex items-start gap-3 p-3 bg-panel-dark rounded-lg border border-panel hover:border-indigo-500/50 transition-colors"
      >
        <div className="flex-shrink-0">
          {isActive ? (
            <div className="w-12 h-12 rounded bg-indigo-500/20 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
            </div>
          ) : thumbnailUrl ? (
            <img
              src={thumbnailUrl}
              alt="Result"
              className="w-12 h-12 rounded object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded bg-green-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-green-400" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-primary truncate">
                {job.generation_type === 'image' ? 'Image' : 'Video'} Generation
              </p>
              <p className="text-xs text-secondary truncate mt-0.5">
                {job.params?.prompt?.substring(0, 50)}
                {job.params?.prompt?.length > 50 ? '...' : ''}
              </p>
            </div>
            {!isActive && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 flex-shrink-0"
                onClick={() => dismissJob(job.id)}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>

          {isActive && (
            <div className="mt-2 space-y-1">
              <Progress value={progress} className="h-1" />
              <div className="flex items-center justify-between text-xs text-secondary">
                <span>{job.status}</span>
                <span>{progress}%</span>
              </div>
            </div>
          )}

          {!isActive && job.result && (
            <div className="mt-2 flex items-center gap-2">
              <Badge variant="outline" className="text-xs bg-green-500/20 text-green-400 border-green-500/30">
                Completed
              </Badge>
              {job.result.seed && (
                <span className="text-xs text-secondary">
                  Seed: {job.result.seed}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-h-[600px] flex flex-col">
      <Card className="glass-panel shadow-2xl border-panel overflow-hidden flex flex-col max-h-full">
        <div
          className="flex items-center justify-between p-3 border-b border-panel cursor-pointer hover:bg-panel-dark transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-medium text-primary">
              Generation Jobs
            </span>
            <Badge variant="secondary" className="h-5 text-xs">
              {totalJobs}
            </Badge>
          </div>

          <div className="flex items-center gap-1">
            {completedJobs.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs"
                onClick={(e) => {
                  e.stopPropagation();
                  dismissAll();
                }}
              >
                Clear All
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronUp className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {isExpanded && (
          <div className="overflow-y-auto flex-1 p-3 space-y-3 max-h-[520px]">
            {activeJobs.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-medium text-secondary uppercase">
                  <Clock className="w-3 h-3" />
                  <span>Active ({activeJobs.length})</span>
                </div>
                {activeJobs.map(job => renderJobItem(job, true))}
              </div>
            )}

            {completedJobs.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-medium text-secondary uppercase">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Completed ({completedJobs.length})</span>
                </div>
                {completedJobs.map(job => renderJobItem(job, false))}
              </div>
            )}
          </div>
        )}

        {!isExpanded && (
          <div className="p-2">
            <div className="text-xs text-secondary text-center">
              {activeJobs.length > 0 && (
                <span>{activeJobs.length} active</span>
              )}
              {activeJobs.length > 0 && completedJobs.length > 0 && <span> • </span>}
              {completedJobs.length > 0 && (
                <span>{completedJobs.length} completed</span>
              )}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default NotificationWidget;
