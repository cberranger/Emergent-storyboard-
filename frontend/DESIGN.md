# Frontend - Design Document

## 1. Overview

The frontend is a React 18 Single Page Application providing professional storyboarding and AI content generation workflows. It includes 76 components (30 feature + 46 UI primitives), centralized API service layer with 8 modules, Shadcn UI component library with Tailwind CSS styling, real-time updates with 5-second polling, complete CRUD operations for all resources, timeline visualization with drag-and-drop, and export to professional video editing formats.

## 2. Design Principles

1. **Component-Based Architecture**: Modular, reusable React components
2. **Service Layer**: Centralized API client for backend communication
3. **Responsive Design**: Mobile-friendly layout with Tailwind CSS
4. **Accessibility**: ARIA labels, keyboard navigation, screen reader support
5. **Professional UI/UX**: Dark theme, consistent styling, intuitive workflows
6. **Performance**: Lazy loading (planned), memoization (planned), code splitting (planned)

## 3. Architecture

### 3.1 Component Diagram

```
React 18 Application
├── Main Components (30)
│   ├── Project Management: ProjectView, ProjectDashboard, ProjectTimeline
│   ├── Scene & Clip Editing: SceneManager, Timeline, UnifiedTimeline
│   ├── Generation: EnhancedGenerationDialog, BatchGenerationDialog, GenerationStudio
│   ├── Library Management: CharacterManager, AdvancedCharacterCreator, StyleTemplateLibrary
│   ├── Queue & Monitoring: QueueDashboard, QueueJobCard, ComfyUIManager
│   ├── Content Reuse: GenerationPool
│   ├── Utilities: PresentationMode, ExportDialog, HotkeyHelpDialog, MediaViewerDialog
│   ├── Face Fusion: FaceFusionProcessor
│   └── Navigation: Sidebar, SceneActionButtons, MetadataItem
├── UI Components (46 Shadcn Primitives)
│   ├── Form Controls: button, input, select, checkbox, radio-group, slider, switch
│   ├── Layout: card, dialog, separator, scroll-area, resizable, sheet, drawer
│   ├── Feedback: toast, alert, badge, progress, skeleton, sonner
│   ├── Navigation: tabs, breadcrumbs, menubar, navigation-menu, context-menu, command
│   ├── Data Display: table, accordion, carousel, calendar, collapsible
│   ├── Overlays: popover, tooltip, hover-card, alert-dialog, dropdown-menu
│   └── Typography: label, text-area
├── API Service Layer (8 modules)
│   ├── Base Client: apiClient (Axios with interceptors)
│   ├── Domain Services: ProjectService, SceneService, ClipService
│   ├── Domain Services: CharacterService, TemplateService, QueueService
│   └── Domain Services: GenerationService, ComfyUIService
├── State Management
│   ├── Current: Props drilling
│   └── Planned: Zustand/Redux Toolkit
└── Utilities
    ├── Config: config.js (centralized configuration)
    ├── Hooks: useHotkeys.js (keyboard shortcuts)
    └── Validators: validators.js (input validation)
```

### 3.2 Data Flow

```
User Interaction
  ↓
Component State Update
  ↓
Service Method Call (e.g., ProjectService.create())
  ↓
apiClient HTTP Request (Axios)
  ↓
Backend API (/api/v1/*)
  ↓
Response Transformation (apiClient interceptors)
  ↓
Service Returns Data
  ↓
Component State Update
  ↓
Re-render UI
```

## 4. Core Components

### 4.1 Project Management Components

**Purpose**: Manage storyboard projects, view project statistics, navigate projects

**Components**:

1. **ProjectView**
   - Purpose: Project listing and creation
   - Location: `src/components/ProjectView.jsx`
   - Features: Grid/list view, search, create dialog, project cards

2. **ProjectDashboard**
   - Purpose: Project stats, music player, settings
   - Location: `src/components/ProjectDashboard.jsx`
   - Features: Stats cards, music player, scene list, settings editor

3. **ProjectTimeline**
   - Purpose: Timeline visualization (Phase 2.6)
   - Location: `src/components/ProjectTimeline.jsx`
   - Features: Horizontal timeline, scene blocks, clip visualization, zoom control

**Interface Definition**:
```jsx
function ProjectDashboard({ project, onRefresh }) {
  const [stats, setStats] = useState(null);
  const [musicPlaying, setMusicPlaying] = useState(false);

  useEffect(() => {
    loadProjectStats();
  }, [project?.id]);

  return (
    <div className="project-dashboard">
      {/* Stats cards */}
      {/* Music player */}
      {/* Scene list */}
    </div>
  );
}
```

### 4.2 Scene & Clip Editing Components

**Purpose**: Create and edit scenes, manage clips on timeline

**Components**:

1. **SceneManager**
   - Purpose: Scene/clip CRUD
   - Location: `src/components/SceneManager.jsx`

2. **Timeline**
   - Purpose: Drag-drop timeline
   - Location: `src/components/Timeline.jsx`

3. **UnifiedTimeline**
   - Purpose: Unified timeline view
   - Location: `src/components/UnifiedTimeline.jsx`

### 4.3 Generation Components

**Purpose**: AI content generation interface, batch generation

**Components**:

1. **EnhancedGenerationDialog**
   - Purpose: Main generation interface
   - Location: `src/components/EnhancedGenerationDialog.jsx`

2. **BatchGenerationDialog**
   - Purpose: Batch generation
   - Location: `src/components/BatchGenerationDialog.jsx`

3. **GenerationStudio**
   - Purpose: Generation workspace
   - Location: `src/components/GenerationStudio.jsx`

### 4.4 Library Management Components

**Purpose**: Manage characters, templates, and models

**Components**:

1. **CharacterManager**
   - Purpose: Character library (Phase 2.5)
   - Location: `src/components/CharacterManager.jsx`

2. **AdvancedCharacterCreator**
   - Purpose: Advanced character creation
   - Location: `src/components/AdvancedCharacterCreator.jsx`

3. **StyleTemplateLibrary**
   - Purpose: Template library (Phase 2.5)
   - Location: `src/components/StyleTemplateLibrary.jsx`

4. **ModelBrowser**
   - Purpose: Model browsing with Civitai integration
   - Location: `src/components/ModelBrowser.jsx`

### 4.5 Queue & Monitoring Components

**Purpose**: Monitor generation queue, manage ComfyUI servers

**Components**:

1. **QueueDashboard**
   - Purpose: Queue monitoring (Phase 2.5)
   - Location: `src/components/QueueDashboard.jsx`

2. **QueueJobCard**
   - Purpose: Job display component
   - Location: `src/components/QueueJobCard.jsx`

3. **ComfyUIManager**
   - Purpose: Server management
   - Location: `src/components/ComfyUIManager.jsx`

### 4.6 Utility Components

**Purpose**: Presentation, export, hotkeys, media viewing

**Components**:

1. **PresentationMode**
   - Purpose: Full-screen presentation
   - Location: `src/components/PresentationMode.jsx`

2. **ExportDialog**
   - Purpose: Export to professional editors
   - Location: `src/components/ExportDialog.jsx`

3. **HotkeyHelpDialog**
   - Purpose: Keyboard shortcuts (40+)
   - Location: `src/components/HotkeyHelpDialog.jsx`

4. **MediaViewerDialog**
   - Purpose: Media viewing
   - Location: `src/components/MediaViewerDialog.jsx`

## 5. Data Models

### 5.1 Project Model (Frontend)

```javascript
{
  id: string,
  name: string,
  description: string | null,
  music_file: string | null,
  created_at: string,
  updated_at: string
}
```

### 5.2 Scene Model (Frontend)

```javascript
{
  id: string,
  project_id: string,
  name: string,
  description: string | null,
  order: number,
  parent_scene_id: string | null,
  alternate_number: number,
  is_alternate: boolean,
  created_at: string,
  updated_at: string
}
```

### 5.3 Clip Model (Frontend)

```javascript
{
  id: string,
  scene_id: string,
  name: string,
  lyrics: string | null,
  image_prompt: string,
  video_prompt: string,
  timeline_position: number,
  length: number,
  character_id: string | null,
  parent_clip_id: string | null,
  alternate_number: number,
  is_alternate: boolean,
  generated_images: GeneratedContent[],
  generated_videos: GeneratedContent[],
  created_at: string,
  updated_at: string
}
```

## 6. API Service Layer

### 6.1 Base Client (apiClient.js)

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: config.backendUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  // Add auth token when available (Phase 3)
  // Add request ID for tracing (Phase 7)
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Centralized error handling
    throw transformError(error);
  }
);
```

### 6.2 Service Modules

| Service | Purpose | Methods |
|--------|---------|---------|
| `ProjectService` | Project operations | create, list, get, update, delete, getWithScenes, getClips |
| `SceneService` | Scene operations | create, list, get, update, delete, getTimelineAnalysis |
| `ClipService` | Clip operations | create, list, get, getGallery, update, updateTimelinePosition, updatePrompts, delete |
| `CharacterService` | Character operations | create, list, get, update, delete, applyToClip |
| `TemplateService` | Template operations | create, list, get, update, delete, use |
| `QueueService` | Queue operations | addJob, listJobs, getJob, getStatus, getProjectJobs, registerServer, getNextJob, completeJob, cancelJob, retryJob, deleteJob, clear |
| `GenerationService` | Generation operations | generate, batch, getBatchStatus, listBatches |
| `ComfyUIService` | ComfyUI operations | addServer, listServers, getServerInfo, updateServer, deleteServer |

## 7. Configuration

### 7.1 Environment Variables

```bash
# Backend API
REACT_APP_BACKEND_URL=http://localhost:8001

# Frontend
PORT=3000
BROWSER=none  # Prevent auto-open on start
```

### 7.2 Centralized Config (config.js)

```javascript
export const config = {
  backendUrl: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
  isProduction: process.env.NODE_ENV === 'production',
  apiTimeout: 30000,
  pollInterval: 5000  // 5 seconds for real-time updates
};

// Validate required config
if (!config.backendUrl) {
  if (config.isProduction) {
    console.error('REACT_APP_BACKEND_URL is required in production');
  }
}
```

## 8. Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `NetworkError` | Backend unreachable | Show error toast with retry option |
| `ValidationError` | Invalid input | Show validation error inline |
| `NotFoundError` | Resource not found | Show "Not found" error, navigate to list |
| `ServerError` | Backend error (5xx) | Show error toast, log to console |

**Error Handling Pattern:**
```javascript
try {
  const project = await ProjectService.create(projectData);
  showToast('Project created successfully', 'success');
  onProjectCreated(project);
} catch (error) {
  if (error.response?.status === 400) {
    showToast(error.response.data.message, 'error');
  } else {
    showToast('Failed to create project', 'error');
  }
}
```

## 9. Performance Considerations

- **Component Memoization**: Use `useMemo` for expensive computations (planned)
- **Callback Optimization**: Use `useCallback` for event handlers (planned)
- **Code Splitting**: Lazy load routes with `React.lazy` (planned)
- **Image Optimization**: Lazy loading, progressive loading, WebP format (planned)
- **Polling Optimization**: 5-second interval for real-time updates
- **Bundle Size**: Optimize with webpack/terser (planned)

## 10. Security Considerations

- **Environment Variables**: Backend URL from REACT_APP_BACKEND_URL
- **CORS**: Backend is allow-all; no origin restrictions
- **XSS Prevention**: React escapes JSX automatically
- **Input Validation**: Validate all user inputs before API calls
- **Planned**: JWT token storage (Phase 3), secure cookie usage (Phase 3)

## 11. Testing Strategy

### Unit Tests (Planned - Phase 8)
- Component rendering with Jest + React Testing Library
- Service layer with mocked Axios responses
- Hooks with `@testing-library/react-hooks`

### Integration Tests (Planned - Phase 8)
- API client integration with mocked backend
- Component integration with mocked services

### E2E Tests (Planned - Phase 8)
- Complete workflows via Playwright
- Cross-browser testing

## 12. Future Considerations

- **State Management**: Migrate to Zustand or Redux Toolkit
- **TypeScript**: Add type safety throughout codebase
- **Code Splitting**: Lazy load routes and large components
- **Performance**: Memoization, virtual scrolling for large lists
- **Testing**: Comprehensive test suite with >80% coverage
- **Accessibility**: Full WCAG 2.1 AA compliance
- **PWA**: Add offline support and installability
- **WebSockets**: Real-time updates instead of polling

---

*Last Updated: December 2024*
*Status: Production-ready with comprehensive component library*
