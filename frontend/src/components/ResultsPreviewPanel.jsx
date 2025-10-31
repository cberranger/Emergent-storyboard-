import React, { useState, useEffect, useRef } from 'react';
import { Eye, Loader2, Image as ImageIcon, Video as VideoIcon, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { clipService } from '@/services';

const ResultsPreviewPanel = ({ clipId, contentType = 'all', limit = 3, onContentClick }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(true);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    if (clipId) {
      fetchResults();
      startPolling();
    }

    return () => {
      stopPolling();
    };
  }, [clipId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const data = await clipService.getClipGallery(clipId);
      
      let combinedResults = [];
      if (contentType === 'all' || contentType === 'image') {
        combinedResults = [...combinedResults, ...(data.images || [])];
      }
      if (contentType === 'all' || contentType === 'video') {
        combinedResults = [...combinedResults, ...(data.videos || [])];
      }

      combinedResults.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setResults(combinedResults.slice(0, limit));
    } catch (error) {
      console.error('Error fetching results:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const startPolling = () => {
    pollIntervalRef.current = setInterval(() => {
      fetchResults();
    }, 5000);
  };

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const togglePolling = () => {
    if (polling) {
      stopPolling();
      setPolling(false);
    } else {
      startPolling();
      setPolling(true);
    }
  };

  const renderContentPreview = (content) => {
    if (content.content_type === 'image') {
      return (
        <div className="relative aspect-video bg-slate-100 rounded overflow-hidden">
          <img
            src={content.url}
            alt="Generated"
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.parentElement.classList.add('flex', 'items-center', 'justify-center');
              e.target.parentElement.innerHTML = '<div class="text-gray-400 text-xs">Failed to load</div>';
            }}
          />
          <Badge className="absolute top-2 right-2 bg-blue-500 text-white text-xs">
            <ImageIcon className="w-3 h-3 mr-1" />
            Image
          </Badge>
        </div>
      );
    }

    if (content.content_type === 'video') {
      return (
        <div className="relative aspect-video bg-slate-100 rounded overflow-hidden">
          <video
            src={content.url}
            className="w-full h-full object-cover"
            controls
            muted
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.parentElement.classList.add('flex', 'items-center', 'justify-center');
              e.target.parentElement.innerHTML = '<div class="text-gray-400 text-xs">Failed to load</div>';
            }}
          />
          <Badge className="absolute top-2 right-2 bg-purple-500 text-white text-xs">
            <VideoIcon className="w-3 h-3 mr-1" />
            Video
          </Badge>
        </div>
      );
    }

    return null;
  };

  if (loading && results.length === 0) {
    return (
      <Card className="bg-white border-slate-200">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-slate-800">
            Recent Results
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white border-slate-200 h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-slate-800">
            Recent Results
          </CardTitle>
          <button
            onClick={togglePolling}
            className={`p-1 rounded hover:bg-slate-100 transition-colors ${polling ? 'text-green-600' : 'text-gray-400'}`}
            title={polling ? 'Stop auto-refresh' : 'Start auto-refresh'}
          >
            <RefreshCw className={`w-4 h-4 ${polling ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {results.length === 0 ? (
          <div className="text-center py-12">
            <Eye className="w-12 h-12 text-gray-400 mx-auto mb-2 opacity-50" />
            <p className="text-sm text-gray-500">No results yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Generated content will appear here
            </p>
          </div>
        ) : (
          results.map((content, index) => (
            <div
              key={content.id}
              className="cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => onContentClick && onContentClick(content)}
            >
              {renderContentPreview(content)}
              <div className="mt-2 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-700">
                    {content.model_name || 'Unknown model'}
                  </span>
                  {content.is_selected && (
                    <Badge variant="outline" className="text-xs">Selected</Badge>
                  )}
                </div>
                {content.prompt && (
                  <p className="text-xs text-gray-500 line-clamp-2">
                    {content.prompt}
                  </p>
                )}
                <p className="text-xs text-gray-400">
                  {new Date(content.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
};

export default ResultsPreviewPanel;
