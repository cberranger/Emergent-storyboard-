import React, { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { API } from "@/config";

// Import components
import Sidebar from "@/components/Sidebar";
import ProjectView from "@/components/ProjectView";
import ComfyUIManager from "@/components/ComfyUIManager";
import Timeline from "@/components/Timeline";
import ProjectTimeline from "@/components/ProjectTimeline";
import UnifiedTimeline from "@/components/UnifiedTimeline";
import CharacterManager from "@/components/CharacterManager";
import StyleTemplateLibrary from "@/components/StyleTemplateLibrary";
import QueueDashboard from "@/components/QueueDashboard";
import GenerationPool from "@/components/GenerationPool";
import ProjectDashboard from "@/components/ProjectDashboard";

function App() {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [comfyUIServers, setComfyUIServers] = useState([]);
  const [currentView, setCurrentView] = useState('projects'); // 'projects', 'timeline', 'project-timeline', 'comfyui'
  const [loading, setLoading] = useState(true);
  const [activeScene, setActiveScene] = useState(null);
  const [activeClip, setActiveClip] = useState(null);

  // Fetch projects on load
  useEffect(() => {
    fetchProjects();
    fetchComfyUIServers();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchComfyUIServers = async () => {
    try {
      const response = await axios.get(`${API}/comfyui/servers`);
      setComfyUIServers(response.data);
    } catch (error) {
      console.error('Error fetching ComfyUI servers:', error);
    }
  };

  const createProject = async (name, description) => {
    try {
      const response = await axios.post(`${API}/projects`, {
        name,
        description
      });
      setProjects([...projects, response.data]);
      toast.success('Project created successfully');
      return response.data;
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
      return null;
    }
  };

  const addComfyUIServer = async () => {
    // This will be handled by the ComfyUIManager component directly
    fetchComfyUIServers(); // Just refresh the list
  };

  const selectProject = (project) => {
    setActiveProject(project);
    setCurrentView('project-timeline'); // Start with project-level timeline
  };

  const handleSceneClick = (scene) => {
    setActiveScene(scene);
    setCurrentView('timeline'); // Scene detail view
  };

  const handleClipClick = (clip) => {
    setActiveClip(clip);
    // Could add clip detail view here in future
  };

  const renderMainContent = () => {
    switch (currentView) {
      case 'projects':
        return (
          <ProjectView
            projects={projects}
            onCreateProject={createProject}
            onSelectProject={selectProject}
            loading={loading}
          />
        );
      case 'project-dashboard':
        return activeProject ? (
          <ProjectDashboard
            project={activeProject}
            onProjectUpdate={fetchProjects}
            onSceneSelect={handleSceneClick}
          />
        ) : (
          <Navigate to="/projects" />
        );
      case 'project-timeline':
        return activeProject ? (
          <ProjectTimeline
            project={activeProject}
            onSceneClick={handleSceneClick}
            onClipClick={handleClipClick}
          />
        ) : (
          <Navigate to="/projects" />
        );
      case 'timeline':
        return activeProject ? (
          <UnifiedTimeline
            project={activeProject}
            comfyUIServers={comfyUIServers}
          />
        ) : (
          <Navigate to="/projects" />
        );
      case 'characters':
        return <CharacterManager activeProject={activeProject} />;
      case 'templates':
        return <StyleTemplateLibrary activeProject={activeProject} />;
      case 'pool':
        return <GenerationPool project={activeProject} />;
      case 'queue':
        return <QueueDashboard />;
      case 'comfyui':
        return (
          <ComfyUIManager
            servers={comfyUIServers}
            onAddServer={addComfyUIServer}
            onRefresh={fetchComfyUIServers}
          />
        );
      default:
        return <ProjectView projects={projects} onCreateProject={createProject} onSelectProject={selectProject} loading={loading} />;
    }
  };

  return (
    <BrowserRouter>
      <div className="App flex h-screen bg-gray-900 text-white">
        <Sidebar
          currentView={currentView}
          onViewChange={setCurrentView}
          activeProject={activeProject}
          onProjectSelect={() => setCurrentView('projects')}
        />
        
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route
              path="/*"
              element={renderMainContent()}
            />
          </Routes>
        </main>
        
        <Toaster theme="dark" />
      </div>
    </BrowserRouter>
  );
}

export default App;