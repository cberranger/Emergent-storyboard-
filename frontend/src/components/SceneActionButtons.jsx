import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

const SceneActionButtons = ({ 
  onAddClip, 
  onCreateAlternate, 
  addClipText = "Clip",
  addClipClassName = "h-6 px-2 text-xs hover:bg-slate-100",
  alternateClassName = "h-5 w-5 p-0 hover:bg-slate-200"
}) => {
  return (
    <div className="flex items-center space-x-1">
      <Button
        variant="outline"
        size="sm"
        onClick={onAddClip}
        className={addClipClassName}
        title="Add new clip"
      >
        <Plus className="w-3 h-3 mr-1" />
        {addClipText}
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={onCreateAlternate}
        className={alternateClassName}
        title="Create alternate"
      >
        <Plus className="w-3 h-3" />
      </Button>
    </div>
  );
};

export default SceneActionButtons;
