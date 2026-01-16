# StoryCanvas - AI Storyboarding Application

> ⚠️ **AGENT NOTICE**: Read [AGENT_RULES.md](AGENT_RULES.md) first. Those rules are mandatory.

## Project Overview

StoryCanvas is a professional AI-powered storyboarding application with ComfyUI integration for generating images and videos. The platform provides a structured workflow for animation production from concept to final export, featuring hierarchical project and scene organization, reusable character and style template configuration, automated content generation through ComfyUI and OpenAI services, timeline-based editing with clip positioning, intelligent queue management for distributing workloads across multiple ComfyUI servers, and export capabilities to professional video editing formats including Final Cut Pro XML, Adobe Premiere EDL, and DaVinci Resolve.

### Key Principles

- **Clean Architecture**: Service layer abstraction, repository pattern, DTO validation, and proper separation of concerns
- **API Versioning**: Versioned endpoints under `/api/v1` with backward compatibility maintained
- **Type Safety**: Comprehensive Pydantic models for backend, centralized API service layer for frontend
- **User Experience**: Professional dark theme, keyboard shortcuts, real-time updates, and accessible UI components
- **Scalability**: Smart queue management with load balancing, multi-server support, and extensible model preset system

## CORS Policy

CORS is fully neutralized across all environments. Allow all origins, methods, and headers, with no origin gating or restrictions.

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   API Layer  │────▶│   Services  │────▶│ Repositories│
│    React    │     │  (FastAPI)   │     │  (Business) │     │  (MongoDB)  │
│   + Shadcn  │     │  /api/v1/*   │     │     Logic   │     │             │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
        │                   │                    │                    │
        │                   │                    ▼                    ▼
        │                   │              ┌──────────┐      ┌──────────┐
        │                   │              │ ComfyUI  │      │  OpenAI  │
        │                   │              │ Services │      │  Video   │
        │                   │              │ (Multi)  │      │ Service  │
        │                   │              └──────────┘      └──────────┘
        │                   │                    │
        │                   └────────────────────┼────────────────────┐
        │                                        │                    │
        ▼                                        ▼                    ▼
  ┌───────────┐                          ┌───────────┐        ┌───────────┐
  │   Queue   │                          │   Queue   │        │  Export   │
  │ Manager   │                          │ Dashboard │        │ Service   │
  └───────────┘                          └───────────┘        └───────────┘
```

## Directory Structure

```
storycanvas/
├── AGENT_RULES.md          # Universal operating rules (this file reference)
├── AGENTS.md               # This file (root project overview)
├── TASKS.md                # Master task list with phases
├── backend/                # FastAPI backend
│   ├── AGENTS.md           # Backend component context
│   ├── DESIGN.md           # Backend technical specification
│   ├── TASKS.md            # Backend development tasks
│   ├── api/v1/            # Versioned API routers (11 routers, 61 endpoints)
│   ├── services/           # Business logic layer (10+ services)
│   ├── repositories/       # Data access layer (4 repositories)
│   ├── dtos/               # Data transfer objects (42+ classes)
│   ├── models/             # Pydantic models
│   ├── utils/              # Utilities
│   ├── database.py         # Database manager
│   ├── config.py           # Configuration
│   └── server.py          # Main application
├── frontend/               # React frontend
│   ├── AGENTS.md           # Frontend component context
│   ├── DESIGN.md           # Frontend technical specification
│   ├── TASKS.md            # Frontend development tasks
│   ├── src/
│   │   ├── components/     # 76 React components (30 feature + 46 UI)
│   │   ├── services/       # API client layer (8 services)
│   │   ├── hooks/          # Custom React hooks
│   │   └── App.js         # Root component
│   └── package.json
├── docs/                   # Documentation
│   ├── archive/            # Completed phase docs
│   ├── CURRENT_STATUS.md
│   ├── CHARACTER_CREATION_BEST_PRACTICES.md
│   ├── FACEFUSION_INTEGRATION.md
│   └── DATABASE_SCHEMA.md
├── launch.ps1              # PowerShell launcher
└── launch.bat              # Batch launcher
```

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| backend | FastAPI backend with MongoDB, service layer, repository pattern, API versioning | Production-ready |
| frontend | React frontend with Shadcn UI, real-time updates, keyboard shortcuts | Production-ready |
| docs | Project documentation, archived phase completions, technical guides | Active |

## Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend API** | FastAPI (Python 3.8+) | Fast async support, automatic docs, type validation |
| **Database** | MongoDB with Motor | Flexible schema for complex nested structures, async driver |
| **Frontend** | React 18 + Shadcn UI | Component ecosystem, dark theme, accessibility |
| **State** | Props (planned: Zustand/Redux) | Simple state, future improvements planned |
| **API Client** | Axios | HTTP client with interceptors, centralized error handling |
| **ComfyUI** | Direct API + RunPod Serverless | Local and cloud generation support |
| **File Uploads** | FastAPI UploadFile | Native multipart handling with validation |
| **Queue Management** | In-memory (planned: Redis) | Simple queue for single-server, planned scale |
| **Export Formats** | FCPXML, EDL, XML, JSON | Professional video editor formats |
| **Logging** | Python logging (planned: structlog) | Basic logging, future observability |
| **Testing** | Planned (pytest, Jest, Playwright) | No automated tests yet (Phase 8) |

## Canonical Names (Locked)

| Concept | Canonical Name | NOT |
|---------|---------------|-----|
| Storyboard Project | `Project` | Story, Animation, Video |
| Scene | `Scene` | Chapter, Segment, Part |
| Timeline Clip | `Clip` | Frame, Shot, Asset |
| Character Template | `Character` | Persona, Actor, Model |
| Style Template | `StyleTemplate` | Template, Preset, Style |
| Generation Job | `QueueJob` | Job, Task, Request |
| AI Model Configuration | `ModelConfig` | Preset, Config, Settings |
| Generated Content | `GeneratedContent` | Asset, Media, Result |

## Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p50) | < 200ms |
| API Response Time (p95) | < 500ms |
| API Response Time (p99) | < 1000ms |
| Generation Queue Throughput | > 10 jobs/min per server |
| Frontend Initial Load | < 3s |
| Frontend Route Change | < 500ms |
| Database Query Time (p95) | < 100ms |
| Test Coverage | > 80% |

## Hardware/Environment

### Development
- **OS**: Windows 10/11 (primary), Linux/macOS compatible
- **Node.js**: v16+ (for frontend)
- **Python**: 3.8+ (for backend)
- **MongoDB**: Community Server 6.0+ or MongoDB Atlas
- **ComfyUI**: Local Docker/Unraid or RunPod Serverless

### Production (Recommended)
- **Backend Server**: 4+ CPU cores, 8GB RAM, SSD storage
- **Database**: MongoDB Atlas (M30+ for production) or dedicated server
- **Frontend**: Static hosting (Vercel, Netlify) or CDN
- **ComfyUI**: GPU-enabled servers (RTX 3060+ or cloud GPU instances)
- **Redis**: For caching and queue management (planned)

## Related Resources

- [AGENT_RULES.md](AGENT_RULES.md) - Universal operating rules (READ THIS FIRST)
- [backend/AGENTS.md](backend/AGENTS.md) - Backend component context
- [backend/DESIGN.md](backend/DESIGN.md) - Backend technical specification
- [backend/TASKS.md](backend/TASKS.md) - Backend development tasks
- [frontend/AGENTS.md](frontend/AGENTS.md) - Frontend component context
- [frontend/DESIGN.md](frontend/DESIGN.md) - Frontend technical specification
- [frontend/TASKS.md](frontend/TASKS.md) - Frontend development tasks
- [TASKS.md](TASKS.md) - Master task list with phases

## Quick Start for Agents

1. **Read AGENT_RULES.md** first to understand universal operating rules
2. **Read this file (AGENTS.md)** to understand the project context
3. **Read TASKS.md** to see the current task list and priorities
4. **Navigate to component documentation** (backend/AGENTS.md or frontend/AGENTS.md) for component-specific context
5. **Read DESIGN.md** for the component you're working on to understand the technical specification
6. **Start working on the first unchecked task** in the component's TASKS.md

## Current Status (December 2024)

- ✅ **Phase 1**: Critical bug fixes (database, CORS neutralization, validation)
- ✅ **Phase 2**: Architecture improvements (service layer, repositories, DTOs, API versioning)
- ✅ **Phase 2.5**: Frontend-backend integration (Characters, Templates, Queue, Project Dashboard)
- ✅ **Phase 2.6**: Timeline system with alternates
- ✅ **Phase 2.7**: Generation pool for content reuse
- 📋 **Phase 3**: Security & Authentication (planned)
- 📋 **Phase 4**: Content features (partial completion)
- 📋 **Phase 5**: Frontend improvements (planned)
- 📋 **Phase 6**: Data management (planned)
- 📋 **Phase 7**: Monitoring & observability (planned)
- 📋 **Phase 8**: Testing & CI/CD (planned)

---

*Last Updated: December 2024*
*Architecture Phase: Production-ready with clean architecture*
*Next Priority: Phase 3 - Security & Authentication*
