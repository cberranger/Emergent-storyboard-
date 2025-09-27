import React from 'react';
import { Film, Server, FolderOpen, Clock, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Sidebar = ({ currentView, onViewChange, activeProject, onProjectSelect }) => {
  const menuItems = [
    {
      id: 'projects',
      label: 'Projects',
      icon: FolderOpen,
      description: 'Manage your storyboard projects'
    },
    {
      id: 'timeline',
      label: 'Timeline',
      icon: Timeline,
      description: 'Edit clips and sequences',
      disabled: !activeProject
    },
    {
      id: 'comfyui',
      label: 'ComfyUI Servers',
      icon: Server,
      description: 'Manage generation servers'
    }
  ];

  return (
    <div className="w-64 bg-panel border-r border-panel flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-panel">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Film className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-primary">StoryCanvas</h1>
            <p className="text-xs text-secondary">AI Storyboarding</p>
          </div>
        </div>
      </div>

      {/* Active Project */}
      {activeProject && (
        <div className="p-4 bg-panel-dark border-b border-panel">
          <div className="text-xs text-secondary mb-1">Active Project</div>
          <button 
            onClick={onProjectSelect}
            className="text-left w-full group"
          >
            <div className="text-sm font-medium text-primary group-hover:text-indigo-400 transition-colors">
              {activeProject.name}
            </div>
            <div className="text-xs text-secondary truncate">
              {activeProject.description || 'No description'}
            </div>
          </button>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          const isDisabled = item.disabled;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? "default" : "ghost"}
              className={`w-full justify-start h-auto p-3 ${
                isActive 
                  ? 'bg-indigo-600 hover:bg-indigo-700 text-white' 
                  : 'text-secondary hover:text-primary hover:bg-panel-dark'
              } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => !isDisabled && onViewChange(item.id)}
              disabled={isDisabled}
              data-testid={`sidebar-${item.id}-btn`}
            >
              <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
              <div className="text-left">
                <div className="text-sm font-medium">{item.label}</div>
                <div className="text-xs opacity-75">{item.description}</div>
              </div>
            </Button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-panel">
        <Button 
          variant="ghost" 
          size="sm" 
          className="w-full justify-start text-secondary hover:text-primary"
          data-testid="sidebar-settings-btn"
        >
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;