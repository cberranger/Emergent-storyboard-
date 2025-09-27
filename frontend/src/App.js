import React, { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

// Import components
import Sidebar from "./components/Sidebar";
import ProjectView from "./components/ProjectView";
import ComfyUIManager from "./components/ComfyUIManager";
import Timeline from "./components/Timeline";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [comfyUIServers, setComfyUIServers] = useState([]);
  const [currentView, setCurrentView] = useState('projects'); // 'projects', 'timeline', 'comfyui'
  const [loading, setLoading] = useState(true);

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

  const addComfyUIServer = async (name, url) => {
    try {
      const response = await axios.post(`${API}/comfyui/servers`, {
        name,
        url
      });
      setComfyUIServers([...comfyUIServers, response.data]);
      toast.success('ComfyUI server added successfully');
      return response.data;
    } catch (error) {
      console.error('Error adding ComfyUI server:', error);
      toast.error('Failed to add ComfyUI server');
      return null;
    }
  };

  const selectProject = (project) => {
    setActiveProject(project);
    setCurrentView('timeline');
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
      case 'timeline':
        return activeProject ? (
          <Timeline
            project={activeProject}
            comfyUIServers={comfyUIServers}
          />
        ) : (
          <Navigate to="/projects" />
        );
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