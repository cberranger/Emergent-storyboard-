import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// Info row component for key-value pairs
export function InfoRow({ label, value, className = "" }) {
  return (
    <div className={`flex justify-between ${className}`}>
      <span className="text-secondary">{label}:</span>
      <span className="ml-2">{value}</span>
    </div>
  );
}

// Stats card component for displaying statistics
export function StatsCard({ title, stats, children }) {
  return (
    <Card className="bg-gray-100/5 border-gray-700/30">
      <CardContent className="p-3">
        {title && <h4 className="font-medium mb-2">{title}</h4>}
        {stats ? (
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(stats).map(([key, value]) => (
              <InfoRow key={key} label={key} value={value} />
            ))}
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
}

// Model version card component
export function ModelVersionCard({ version }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'N/A';
    }
  };

  return (
    <Card className="bg-gray-100/5 border-gray-700/30">
      <CardContent className="p-2">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <p className="font-medium text-sm mb-1">{version.name}</p>
            <div className="grid grid-cols-3 gap-2 text-xs text-secondary">
              <div>
                <span className="font-medium">Base:</span> {version.baseModel || 'N/A'}
              </div>
              <div>
                <span className="font-medium">Downloads:</span> {version.stats?.downloadCount?.toLocaleString() || 'N/A'}
              </div>
              <div>
                <span className="font-medium">Published:</span> {formatDate(version.publishedAt)}
              </div>
            </div>
          </div>
          <Badge variant="outline" className="text-xs ml-3">
            {version.nsfwLevel || 'N/A'}
          </Badge>
        </div>
        {version.files && version.files.length > 0 && (
          <div className="mt-2 text-xs text-secondary">
            <span className="font-medium">Files:</span> {version.files.map(f => f.name).join(', ')}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Section header component
export function SectionHeader({ title, className = "" }) {
  return (
    <h4 className={`font-medium text-primary mb-2 ${className}`}>
      {title}
    </h4>
  );
}

// Permissions grid component
export function PermissionsGrid({ permissions }) {
  return (
    <Card className="bg-gray-100/5 border-gray-700/30">
      <CardContent className="p-3">
        <SectionHeader>Usage Permissions</SectionHeader>
        <div className="grid grid-cols-2 gap-2 text-sm">
          {Object.entries(permissions).map(([key, value]) => (
            <InfoRow key={key} label={key} value={value} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// Search result item component
export function SearchResultItem({ result, onSelect }) {
  const model = result.civitai_model;
  
  return (
    <Card 
      className="bg-gray-100/5 border-gray-700/30 cursor-pointer hover:bg-gray-100/10 transition-colors"
      onClick={() => onSelect(model)}
    >
      <CardContent className="p-3">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h5 className="font-medium text-primary">
              {model.name}
            </h5>
            <p className="text-sm text-secondary mt-1 line-clamp-2">
              {model.description?.substring(0, 150)}...
            </p>
            <div className="flex items-center space-x-4 mt-2 text-xs text-secondary">
              <span>Type: {model.type}</span>
              <span>Base: {model.baseModel}</span>
              <span>Score: {(result.match_score * 100).toFixed(0)}%</span>
            </div>
          </div>
          <Badge variant="outline" className="ml-3">
            {(result.match_score * 100).toFixed(0)}%
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

// Metadata grid component
export function MetadataGrid({ metadata, columns = 2 }) {
  return (
    <div className={`grid grid-cols-${columns} gap-2 text-sm`}>
      {Object.entries(metadata).map(([key, value]) => (
        <InfoRow key={key} label={key} value={value} />
      ))}
    </div>
  );
}
