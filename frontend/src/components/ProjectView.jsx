import React, { useState } from 'react';
import { Plus, FolderOpen, Music, Clock, Calendar } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

const ProjectView = ({ projects, onCreateProject, onSelectProject, loading }) => {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newProject.name.trim()) return;
    
    const project = await onCreateProject(newProject.name, newProject.description);
    if (project) {
      setNewProject({ name: '', description: '' });
      setIsCreateOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <div className="h-8 w-48 loading-shimmer rounded mb-4"></div>
            <div className="h-4 w-96 loading-shimmer rounded"></div>
          </div>
          <div className="grid-responsive">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass-panel p-6">
                <div className="h-6 w-3/4 loading-shimmer rounded mb-4"></div>
                <div className="h-4 w-full loading-shimmer rounded mb-2"></div>
                <div className="h-4 w-2/3 loading-shimmer rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-primary mb-2">Projects</h1>
              <p className="text-secondary">Create and manage your storyboard projects</p>
            </div>
            
            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogTrigger asChild>
                <Button className="btn-primary" data-testid="create-project-btn">
                  <Plus className="w-5 h-5 mr-2" />
                  New Project
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-panel border-panel">
                <DialogHeader>
                  <DialogTitle className="text-primary">Create New Project</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateProject} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Project Name
                    </label>
                    <Input
                      className="form-input"
                      placeholder="Enter project name"
                      value={newProject.name}
                      onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                      required
                      data-testid="project-name-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Description
                    </label>
                    <Textarea
                      className="form-input min-h-[100px]"
                      placeholder="Enter project description"
                      value={newProject.description}
                      onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                      data-testid="project-description-input"
                    />
                  </div>
                  <div className="flex justify-end space-x-3 pt-4">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setIsCreateOpen(false)}
                      className="btn-secondary"
                      data-testid="cancel-project-btn"
                    >
                      Cancel
                    </Button>
                    <Button 
                      type="submit" 
                      className="btn-primary"
                      data-testid="submit-project-btn"
                    >
                      Create Project
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Projects Grid */}
          {projects.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-panel-dark flex items-center justify-center">
                <FolderOpen className="w-12 h-12 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold text-primary mb-2">No projects yet</h3>
              <p className="text-secondary mb-6">Create your first storyboard project to get started</p>
              <Button 
                onClick={() => setIsCreateOpen(true)} 
                className="btn-primary"
                data-testid="empty-create-project-btn"
              >
                <Plus className="w-5 h-5 mr-2" />
                Create Project
              </Button>
            </div>
          ) : (
            <div className="grid-responsive animate-fade-in">
              {projects.map((project, index) => (
                <Card 
                  key={project.id} 
                  className="glass-panel hover:bg-opacity-80 transition-all duration-300 cursor-pointer group"
                  onClick={() => onSelectProject(project)}
                  data-testid={`project-card-${index}`}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-primary group-hover:text-indigo-400 transition-colors">
                          {project.name}
                        </CardTitle>
                        {project.description && (
                          <p className="text-sm text-secondary mt-1 line-clamp-2">
                            {project.description}
                          </p>
                        )}
                      </div>
                      <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0 ml-3">
                        <FolderOpen className="w-5 h-5 text-white" />
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        {project.music_file_path && (
                          <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                            <Music className="w-3 h-3 mr-1" />
                            Music
                          </Badge>
                        )}
                        <div className="flex items-center text-secondary">
                          <Calendar className="w-3 h-3 mr-1" />
                          {new Date(project.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectView;