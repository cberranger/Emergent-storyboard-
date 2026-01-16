# Frontend - Development Guide

> ⚠️ **AGENT NOTICE**: Read [../AGENT_RULES.md](../AGENT_RULES.md) first. Follow TASKS.md exactly.

## Overview

The frontend is a React 18 SPA with Shadcn UI components providing professional storyboarding and AI content generation workflows. It includes 76 components (30 feature + 46 UI primitives), centralized API service layer with 8 modules for backend communication, professional dark theme with accessibility support, real-time updates with 5-second polling, complete CRUD operations for projects, scenes, clips, characters, templates, and queue management. The application supports timeline visualization with drag-and-drop, model browsing with Civitai integration, batch generation dialogs, media viewers, and export to professional video editing formats.

## CORS Policy

Backend CORS is intentionally allow-all. Do not add origin restrictions or client-side CORS workarounds.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      React 18 Application                     │
├─────────────────────────────────────────────────────────────────┤
│  Main Components (30)                                        │
│  ├─ ProjectView.jsx              # Project management          │
│  ├─ ProjectDashboard.jsx         # Stats & overview            │
│  ├─ ProjectTimeline.jsx          # Timeline visualization       │
│  ├─ SceneManager.jsx             # Scene/clip editor         │
│  ├─ Timeline.jsx                # Drag-drop timeline         │
│  ├─ UnifiedTimeline.jsx          # Unified timeline view      │
│  ├─ CharacterManager.jsx         # Character library         │
│  ├─ AdvancedCharacterCreator.jsx # Advanced character create  │
│  ├─ StyleTemplateLibrary.jsx     # Template management        │
│  ├─ QueueDashboard.jsx           # Queue monitoring          │
│  ├─ GenerationPool.jsx           # Content reuse library     │
│  ├─ EnhancedGenerationDialog.jsx # Generation interface       │
│  ├─ BatchGenerationDialog.jsx    # Batch generation         │
│  ├─ ComfyUIManager.jsx          # Server management        │
│  ├─ ModelBrowser.jsx            # Model browsing            │
│  ├─ PresentationMode.jsx        # Full-screen presentation  │
│  ├─ ExportDialog.jsx            # Export to editors        │
│  ├─ HotkeyHelpDialog.jsx        # Keyboard shortcuts       │
│  ├─ MediaViewerDialog.jsx       # Media viewing            │
│  ├─ FaceFusionProcessor.jsx    # Face fusion              │
│  ├─ SceneActionButtons.jsx      # Scene operations         │
│  ├─ Sidebar.jsx                # Navigation sidebar        │
│  ├─ MetadataItem.jsx            # Metadata display         │
│  └─ ... (5 more components)                                  │
├─────────────────────────────────────────────────────────────────┤
│  UI Components (46 Shadcn primitives)                       │
│  ├─ button, card, dialog, dropdown-menu, select            │
│  ├─ toast, table, tabs, input, alert, badge, checkbox    │
│  ├─ radio-group, slider, switch, accordion, alert-dialog   │
│  ├─ aspect-ratio, avatar, breadcrumb, calendar, carousel    │
│  ├─ collapsible, command, context-menu, drawer, form      │
│  ├─ hover-card, input-otp, label, menubar               │
│  ├─ navigation-menu, pagination, popover, progress          │
│  ├─ resizable, scroll-area, separator, sheet              │
│  ├─ skeleton, sonner, textarea, toggle                   │
│  ├─ toggle-group, tooltip, toaster                        │
│  └─ ... (5 more UI primitives)                             │
├─────────────────────────────────────────────────────────────────┤
│  API Service Layer (8 modules)                                │
│  ├─ apiClient.js               # Axios base client          │
│  ├─ ProjectService.js          # Project operations (7)     │
│  ├─ SceneService.js            # Scene operations (6)       │
│  ├─ ClipService.js             # Clip operations (8)        │
│  ├─ CharacterService.js        # Character operations (6)   │
│  ├─ TemplateService.js         # Template operations (6)    │
│  ├─ QueueService.js           # Queue operations (12)     │
│  ├─ GenerationService.js       # Generation operations (4)  │
│  └─ ComfyUIService.js         # ComfyUI operations (5)   │
├─────────────────────────────────────────────────────────────────┤
│  Utilities & Hooks                                         │
│  ├─ config.js                 # Centralized configuration  │
│  ├─ useHotkeys.js             # Keyboard shortcut hook    │
│  └─ validators.js             # Input validation         │
├─────────────────────────────────────────────────────────────────┤
│  State Management                                         │
│  ├─ Props drilling (current)                                │
│  └─ Planned: Zustand/Redux Toolkit                          │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Aspect | Choice | Notes |
|--------|--------|-------|
| **Framework** | React 18 | Hooks, functional components |
| **UI Library** | Shadcn UI | Radix UI primitives + Tailwind |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **HTTP Client** | Axios | Interceptors, error handling |
| **State** | Props (planned: Zustand) | Simple state, future improvements |
| **Icons** | Lucide React | Icon library |
| **Routing** | Custom (in App.js) | Component-based routing |
| **Real-time** | Polling (5s) | Planned: WebSockets |

## Key Classes/Modules

| Class/Component | Purpose | Location |
|----------------|---------|----------|
| `ProjectView` | Project listing and creation | `src/components/ProjectView.jsx` |
| `ProjectDashboard` | Stats, music player, settings | `src/components/ProjectDashboard.jsx` |
| `ProjectTimeline` | Timeline visualization (Phase 2.6) | `src/components/ProjectTimeline.jsx` |
| `SceneManager` | Scene/clip CRUD | `src/components/SceneManager.jsx` |
| `Timeline` | Drag-drop timeline | `src/components/Timeline.jsx` |
| `CharacterManager` | Character library (Phase 2.5) | `src/components/CharacterManager.jsx` |
| `AdvancedCharacterCreator` | Advanced character creation | `src/components/AdvancedCharacterCreator.jsx` |
| `StyleTemplateLibrary` | Template library (Phase 2.5) | `src/components/StyleTemplateLibrary.jsx` |
| `QueueDashboard` | Queue monitoring (Phase 2.5) | `src/components/QueueDashboard.jsx` |
| `GenerationPool` | Content reuse library (Phase 2.7) | `src/components/GenerationPool.jsx` |
| `EnhancedGenerationDialog` | Main generation interface | `src/components/EnhancedGenerationDialog.jsx` |
| `BatchGenerationDialog` | Batch generation | `src/components/BatchGenerationDialog.jsx` |
| `ComfyUIManager` | Server management | `src/components/ComfyUIManager.jsx` |
| `ModelBrowser` | Model browsing with Civitai integration | `src/components/ModelBrowser.jsx` |
| `PresentationMode` | Full-screen presentation | `src/components/PresentationMode.jsx` |
| `ExportDialog` | Export to professional editors | `src/components/ExportDialog.jsx` |
| `HotkeyHelpDialog` | Keyboard shortcuts (40+) | `src/components/HotkeyHelpDialog.jsx` |
| `MediaViewerDialog` | Media viewing | `src/components/MediaViewerDialog.jsx` |
| `FaceFusionProcessor` | Face fusion processing | `src/components/FaceFusionProcessor.jsx` |
| `Sidebar` | Navigation sidebar | `src/components/Sidebar.jsx` |
| `ProjectService` | Project operations (7 methods) | `src/services/ProjectService.js` |
| `SceneService` | Scene operations (6 methods) | `src/services/SceneService.js` |
| `ClipService` | Clip operations (8 methods) | `src/services/ClipService.js` |
| `CharacterService` | Character operations (6 methods) | `src/services/CharacterService.js` |
| `TemplateService` | Template operations (6 methods) | `src/services/TemplateService.js` |
| `QueueService` | Queue operations (12 methods) | `src/services/QueueService.js` |
| `GenerationService` | Generation operations (4 methods) | `src/services/GenerationService.js` |
| `ComfyUIService` | ComfyUI operations (5 methods) | `src/services/ComfyUIService.js` |
| `apiClient` | Axios base client with interceptors | `src/services/apiClient.js` |

## Data Flow

1. **User Interaction** → Component state update
2. **Component** → Calls service method (e.g., `ProjectService.create()`)
3. **Service** → Makes API call via `apiClient`
4. **apiClient** → Axios HTTP request to backend (`/api/v1/*`)
5. **Backend** → Processes request → Returns JSON response
6. **apiClient** → Transforms response → Returns to service
7. **Service** → Returns data to component
8. **Component** → Updates state → Re-renders UI

**Example Flow - Create Project:**
```
User clicks "Create Project" button
  ↓
ProjectView state update (open dialog)
  ↓
User fills form → clicks "Save"
  ↓
ProjectService.create(projectData)
  ↓
apiClient.post('/api/v1/projects', projectData)
  ↓
Axios POST request to backend
  ↓
Backend creates project → returns ProjectResponseDTO
  ↓
apiClient.transformResponse(response.data)
  ↓
ProjectService returns project to component
  ↓
ProjectView updates projects list → Re-renders
```

## Configuration

### Environment Variables

```bash
# Backend API
REACT_APP_BACKEND_URL=http://localhost:8001

# Frontend
PORT=3000
```

### Centralized Config (`src/config.js`)

```javascript
export const config = {
  backendUrl: process.env.REACT_APP_BACKEND_URL,
  isProduction: process.env.NODE_ENV === 'production'
};
```

## File Structure

```
frontend/
├── AGENTS.md                   # This file
├── DESIGN.md                   # Technical specification
├── TASKS.md                    # Development tasks
├── src/
│   ├── components/              # 76 React components
│   │   ├── Main Components (30)
│   │   │   ├── ProjectView.jsx
│   │   │   ├── ProjectDashboard.jsx
│   │   │   ├── ProjectTimeline.jsx
│   │   │   ├── SceneManager.jsx
│   │   │   ├── Timeline.jsx
│   │   │   ├── UnifiedTimeline.jsx
│   │   │   ├── TimelineClipCard.jsx
│   │   │   ├── TimelineClipSimple.jsx
│   │   │   ├── CharacterManager.jsx
│   │   │   ├── AdvancedCharacterCreator.jsx
│   │   │   ├── StyleTemplateLibrary.jsx
│   │   │   ├── QueueDashboard.jsx
│   │   │   ├── QueueJobCard.jsx
│   │   │   ├── GenerationPool.jsx
│   │   │   ├── EnhancedGenerationDialog.jsx
│   │   │   ├── GenerationDialog.jsx
│   │   │   ├── GenerationStudio.jsx
│   │   │   ├── BatchGenerationDialog.jsx
│   │   │   ├── ComfyUIManager.jsx
│   │   │   ├── ModelBrowser.jsx
│   │   │   ├── ModelCard.jsx
│   │   │   ├── ModelCardComponents.jsx
│   │   │   ├── PresentationMode.jsx
│   │   │   ├── ExportDialog.jsx
│   │   │   ├── HotkeyHelpDialog.jsx
│   │   │   ├── MediaViewerDialog.jsx
│   │   │   ├── FaceFusionProcessor.jsx
│   │   │   ├── SceneActionButtons.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── MetadataItem.jsx
│   │   └── ui/             # 46 Shadcn components
│   │       ├── button.jsx, card.jsx, dialog.jsx
│   │       ├── dropdown-menu.jsx, select.jsx
│   │       ├── toast.jsx, table.jsx, tabs.jsx
│   │       ├── input.jsx, alert.jsx, badge.jsx
│   │       ├── checkbox.jsx, radio-group.jsx
│   │       ├── slider.jsx, switch.jsx, accordion.jsx
│   │       └── ... (32 more UI primitives)
│   ├── services/              # API client layer (8 services)
│   │   ├── apiClient.js
│   │   ├── ProjectService.js
│   │   ├── SceneService.js
│   │   ├── ClipService.js
│   │   ├── CharacterService.js
│   │   ├── TemplateService.js
│   │   ├── QueueService.js
│   │   ├── GenerationService.js
│   │   └── ComfyUIService.js
│   ├── hooks/                 # Custom React hooks
│   │   └── useHotkeys.js
│   ├── utils/                 # Utilities
│   │   ├── config.js
│   │   └── validators.js
│   └── App.js                 # Root component
├── package.json              # Dependencies
└── .env                     # Environment variables (created by launch script)
```

## Integration Points

| Connects To | Protocol | Data |
|-------------|----------|------|
| **Backend API** | REST/HTTP | JSON (DTOs) |
| **File System** | Browser API | File uploads, downloads |
| **Local Storage** | localStorage | User preferences (planned) |

## Development Setup

1. **Install Node.js v16+**
   ```bash
   node --version  # Should be 16 or higher
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
   ```

4. **Start development server**
   ```bash
   npm start
   # or
   yarn start
   ```

5. **Access application**
   - URL: http://localhost:3000
   - Hot reload: Enabled by default

## Component-to-Feature Mapping

### Project Management
- `ProjectView.jsx` → Project listing and creation
- `ProjectDashboard.jsx` → Stats, music player, settings (uses ProjectService with 7 endpoints)
- `ProjectTimeline.jsx` → Timeline visualization (Phase 2.6)

### Scene & Clip Editing
- `SceneManager.jsx` → Scene/clip CRUD (uses SceneService + ClipService)
- `Timeline.jsx` → Drag-drop timeline
- `UnifiedTimeline.jsx` → Unified timeline
- `TimelineClipCard.jsx`, `TimelineClipSimple.jsx` → Clip visualization

### Generation System
- `EnhancedGenerationDialog.jsx` → Main generation interface (uses GenerationService with 4 endpoints)
- `BatchGenerationDialog.jsx` → Batch generation (backend complete, UI needs multi-select enhancement)
- `GenerationPool.jsx` → Content reuse library (Phase 2.7)

### Library Management
- `CharacterManager.jsx` → Character CRUD (uses CharacterService with 6 endpoints)
- `AdvancedCharacterCreator.jsx` → Advanced character creation
- `StyleTemplateLibrary.jsx` → Template CRUD (uses TemplateService with 6 endpoints)
- `ModelBrowser.jsx` → Model browsing (needs category enhancements)

### Queue & Monitoring
- `QueueDashboard.jsx` → Real-time queue monitoring (uses QueueService with 12 endpoints)
- `QueueJobCard.jsx` → Job display component
- `ComfyUIManager.jsx` → Server management (uses ComfyUIService with 5 endpoints)

### Utilities
- `PresentationMode.jsx` → Full-screen presentation
- `ExportDialog.jsx` → Export to professional editors (uses legacy export endpoints)
- `HotkeyHelpDialog.jsx` → Keyboard shortcuts (40+)
- `MediaViewerDialog.jsx` → Media viewing
- `FaceFusionProcessor.jsx` → Face fusion processing

## Testing

Currently, no automated test suite exists. Test coverage is planned for Phase 8.

**Planned Testing Strategy:**
- Unit tests: Jest + React Testing Library for components
- Integration tests: API client testing with mocked responses
- E2E tests: Playwright for complete workflows

**Manual Testing:**
- Use application UI to test all features
- Monitor browser console for errors
- Test API responses via Network tab in DevTools

## Related Documents

- [../AGENT_RULES.md](../AGENT_RULES.md) - Universal operating rules
- [../AGENTS.md](../AGENTS.md) - Project overview
- [DESIGN.md](DESIGN.md) - Technical specification
- [TASKS.md](TASKS.md) - Development tasks
- [../TASKS.md](../TASKS.md) - Master task list
- [../backend/AGENTS.md](../backend/AGENTS.md) - Backend component context

## Component Inventory (76 Total)

### Main Feature Components (30)
1. ProjectView.jsx
2. ProjectDashboard.jsx
3. ProjectTimeline.jsx
4. SceneManager.jsx
5. Timeline.jsx
6. UnifiedTimeline.jsx
7. TimelineClipCard.jsx
8. TimelineClipSimple.jsx
9. CharacterManager.jsx
10. AdvancedCharacterCreator.jsx
11. StyleTemplateLibrary.jsx
12. QueueDashboard.jsx
13. QueueJobCard.jsx
14. GenerationPool.jsx
15. EnhancedGenerationDialog.jsx
16. GenerationDialog.jsx
17. GenerationStudio.jsx
18. BatchGenerationDialog.jsx
19. ComfyUIManager.jsx
20. ModelBrowser.jsx
21. ModelCard.jsx
22. ModelCardComponents.jsx
23. PresentationMode.jsx
24. ExportDialog.jsx
25. HotkeyHelpDialog.jsx
26. MediaViewerDialog.jsx
27. FaceFusionProcessor.jsx
28. SceneActionButtons.jsx
29. Sidebar.jsx
30. MetadataItem.jsx

### UI Components (46 Shadcn Components)
- button, card, dialog, dropdown-menu, select
- toast, table, tabs, input, alert
- badge, checkbox, radio-group, slider, switch
- accordion, alert-dialog, aspect-ratio, avatar
- breadcrumb, calendar, carousel, collapsible
- command, context-menu, drawer, form
- hover-card, input-otp, label, menubar
- navigation-menu, pagination, popover, progress
- resizable, scroll-area, separator, sheet
- skeleton, sonner, textarea, toggle
- toggle-group, tooltip, toaster

---

*Last Updated: December 2024*
*Status: Production-ready with complete component library*
*Next Priority: Phase 5 - Frontend Improvements (State Management, TypeScript)*
