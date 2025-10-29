import React from 'react';
import { Clock, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const MetadataItem = ({ icon, children, className = "" }) => {
  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      {icon}
      <span>{children}</span>
    </div>
  );
};

const TimelineMetadata = ({ createdAt, completedAt, priority }) => {
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="flex items-center space-x-4 text-xs text-secondary">
      <MetadataItem icon={<Clock className="w-3 h-3" />}>
        Created {formatTimestamp(createdAt)}
      </MetadataItem>
      {completedAt && (
        <MetadataItem icon={<CheckCircle2 className="w-3 h-3" />}>
          Completed {formatTimestamp(completedAt)}
        </MetadataItem>
      )}
      {priority && (
        <Badge variant="outline" className="text-xs">
          Priority: {priority}
        </Badge>
      )}
    </div>
  );
};

export { TimelineMetadata, MetadataItem };
