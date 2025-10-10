import { useState } from 'react';
import { TimelineEditor } from './components/TimelineEditor';
import { Button } from './components/ui/button';
import { Upload, Download, Wand2, Menu } from 'lucide-react';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="h-screen flex flex-col bg-neutral-950 text-white">
      {/* Top Navigation */}
      <header className="flex items-center justify-between px-6 py-3 bg-neutral-900 border-b border-neutral-800">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-lg">StoryCanvas</h1>
            <p className="text-xs text-neutral-400">Timeline Editor - kjk</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Upload className="w-4 h-4 mr-2" />
            Upload Music
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export Project
          </Button>
          <Button size="sm" className="bg-violet-600 hover:bg-violet-700">
            <Wand2 className="w-4 h-4 mr-2" />
            Batch Generate
          </Button>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
            Manage Scenes
          </Button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        {sidebarOpen && (
          <aside className="w-64 bg-neutral-900 border-r border-neutral-800 flex flex-col">
            <nav className="flex-1 p-4 space-y-2">
              <NavItem icon="📁" label="New Project" />
              <NavItem icon="🎬" label="Timeline" active />
              <NavItem icon="👥" label="Characters" sublabel="Build character catalog" />
              <NavItem icon="🎨" label="Style Templates" sublabel="Build and reuse generation styles" />
              <NavItem icon="⏱️" label="Queue Dashboard" sublabel="Monitor generation pipeline" />
              <NavItem icon="🖥️" label="ComfyUI Servers" sublabel="Manage generation servers" />
            </nav>
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          <TimelineEditor />
        </main>
      </div>
    </div>
  );
}

function NavItem({ icon, label, sublabel, active }: { icon: string; label: string; sublabel?: string; active?: boolean }) {
  return (
    <button
      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
        active ? 'bg-violet-600 text-white' : 'hover:bg-neutral-800 text-neutral-300'
      }`}
    >
      <div className="flex items-center gap-3">
        <span className="text-lg">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-sm">{label}</div>
          {sublabel && <div className="text-xs text-neutral-500 truncate">{sublabel}</div>}
        </div>
      </div>
    </button>
  );
}
