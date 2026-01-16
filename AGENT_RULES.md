# Agent Operating Rules

> **This document defines mandatory operating rules for any AI agent working on this project.**
> These rules are universal and apply to all projects. Drop this file into any codebase root.
> Component-specific guidance belongs in each component's AGENTS.md file.

---

## 0. First Steps - Project Bootstrap

### 0.1 Initial Assessment
**Before doing ANY work, check the current directory:**

1. **Does AGENTS.md exist in this directory?**
   - YES → Read it, understand the project/component context
   - NO → Ask user: "No AGENTS.md found. Should I create project documentation structure?" Look to see if there's AGENTS.template.md

2. **Does TASKS.md exist?**
   - YES → This is your work queue. Start from the first unchecked task.
   - NO → Ask user: "No TASKS.md found. What would you like me to work on?"

3. **Does DESIGN.md exist?**
   - YES → Read it before writing any code
   - NO → If tasks require implementation, ask: "No DESIGN.md found. Should I create a technical design first?"

### 0.2 Creating New Project Structure
When user confirms new project setup, create this structure:

```
project-root/
├── AGENT_RULES.md          # This file (copy as-is)
├── AGENTS.md               # Project overview (use template §12.1)
├── ROADMAP.md              # Timeline & milestones (if multi-component)
│
├── component-a/
│   ├── AGENTS.md           # Component context (use template §12.2)
│   ├── DESIGN.md           # Technical spec (use template §12.3)
│   └── TASKS.md            # Task checklist (use template §12.4)
│
└── docs/                   # Only if needed for setup guides, etc.
```

### 0.3 Creating New Component Structure
When adding a component to existing project:

1. Create component directory
2. Create AGENTS.md with component context (template §12.2)
3. Create DESIGN.md with technical design (template §12.3)
4. Create TASKS.md with phased task list (template §12.4)
5. Update root AGENTS.md to reference new component
6. Update ROADMAP.md if timeline implications

---

## 1. Document Hierarchy

### 1.1 Document Purposes

| Document | Scope | Contains | Required |
|----------|-------|----------|----------|
| AGENT_RULES.md | Universal | How to work (process, rules) | Yes - root only |
| AGENTS.md (root) | Project | What we're building (overview, architecture) | Yes |
| ROADMAP.md | Project | When (timeline, dependencies, milestones) | If multi-component |
| AGENTS.md (component) | Component | Context for this specific component | Yes per component |
| DESIGN.md | Component | How it works (technical spec) | Yes per component |
| TASKS.md | Component | What to do (actionable checklist) | Yes per component |

### 1.2 Reading Order for New Agent
1. AGENT_RULES.md (this file) - Understand how to work
2. Root AGENTS.md - Understand what we're building
3. ROADMAP.md - Understand where we are in timeline
4. Component AGENTS.md - Understand this component's role
5. Component DESIGN.md - Understand technical implementation
6. Component TASKS.md - Find your next task

---

## 2. Task Execution Rules

### 2.1 Task List is Source of Truth
- **ALWAYS** work from the component's `TASKS.md` file
- **NEVER** invent tasks not in the task list
- **NEVER** skip tasks or change task order without explicit approval
- If a task is ambiguous, **STOP and ask** before proceeding
- Mark tasks complete (`[x]`) only when fully done and tested

### 2.2 One Task at a Time
- Complete one task fully before starting the next
- "Fully complete" means: code written, tested, documented, committed
- No partial implementations left hanging
- No "I'll come back to this later"

### 2.3 Task Completion Checklist
Before marking any task complete:
- [ ] Code compiles/runs without errors
- [ ] Follows naming conventions (see §4)
- [ ] Matches DESIGN.md specifications exactly
- [ ] Unit tests pass (if applicable)
- [ ] No TODOs or FIXMEs left in code
- [ ] No temporary/debug code remaining
- [ ] No simulated functions, responses, or false operations - all code must be true to its purpose
- [ ] Changes committed with descriptive message

### 2.4 End of Session Housekeeping
Before ending any work session:
- [ ] All files saved
- [ ] No uncommitted changes (or explicitly noted)
- [ ] TASKS.md updated with progress
- [ ] Any blockers documented
- [ ] Clean state - next agent can pick up seamlessly

---

## 3. Decision Making Rules

### 3.1 When to STOP and Ask
**STOP and request human input when:**
- Task requirements are ambiguous
- Multiple valid implementation approaches exist
- Spec doesn't cover an edge case
- You're about to deviate from DESIGN.md
- A dependency is missing or unclear
- You discover a bug in existing code
- Performance target seems unachievable
- You're unsure if something is in scope

**DO NOT:**
- Make architectural decisions silently
- Assume what the human "probably wants"
- Add features not explicitly requested
- "Improve" existing code outside task scope
- Refactor code that's working

### 3.2 Edge Case Handling
When encountering edge cases not covered by spec:
1. **Document the edge case** in a comment
2. **Implement the minimal safe behavior** (fail gracefully, log warning)
3. **Add to TASKS.md** as a new task for review: `- [ ] REVIEW: [description of edge case]`
4. **Continue with main task** - don't rabbit hole

### 3.3 Scope Creep Prevention
If you think "it would be nice to also add X":
- **DON'T** add it
- Note it in TASKS.md under `## Future Enhancements` if truly valuable
- Continue with assigned task

---

## 4. Naming Conventions

### 4.1 File Naming
| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `sensor_hub.py` |
| TypeScript/JS | camelCase files, PascalCase components | `sensorStore.ts`, `SensorCard.tsx` |
| Kotlin/Java | PascalCase | `SensorManager.kt` |
| C#/.NET | PascalCase | `ServerConnection.cs` |
| Config files | kebab-case or lowercase | `docker-compose.yml`, `config.yaml` |
| Documentation | UPPER_CASE.md or kebab-case.md | `AGENTS.md`, `sensor-setup.md` |

### 4.2 Code Naming
| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `SensorHub`, `DataProcessor` |
| Functions/methods | snake_case (Python), camelCase (JS/TS/C#/Kotlin) | `process_frame()`, `processFrame()` |
| Constants | UPPER_SNAKE_CASE | `MAX_FRAME_RATE`, `DEFAULT_PORT` |
| Variables | snake_case (Python), camelCase (JS/TS/C#/Kotlin) | `frame_count`, `frameCount` |
| Type aliases | PascalCase | `FrameCallback`, `SensorConfig` |

### 4.3 Canonical Names
Projects should define locked canonical names in root AGENTS.md under `## Canonical Names`.
When defined, use them exactly - do not invent synonyms.

---

## 5. Documentation Rules

### 5.1 Required Documentation
Each component requires exactly:
- `AGENTS.md` - Component context and guidance
- `DESIGN.md` - Technical architecture and specifications  
- `TASKS.md` - Development task list with checkboxes

### 5.2 Prohibited Documentation
**DO NOT create without explicit approval:**
- README.md files (unless explicitly in task list)
- CHANGELOG.md (git history is the changelog)
- CONTRIBUTING.md
- Additional markdown files
- Duplicate documentation

### 5.3 Documentation Updates
- Update TASKS.md immediately when completing tasks
- Update DESIGN.md only if implementation differs from spec (with approval)
- Never create new documentation files without explicit approval

### 5.4 Comment Style
```python
# GOOD: Explains WHY
# Limit to 3 retries to prevent infinite loops on flaky connections
for attempt in range(3):

# BAD: Restates the obvious  
# Loop 3 times
for attempt in range(3):

# BAD: Vague TODO
# TODO: fix this

# GOOD: Specific TODO
# TODO(#42): Handle reconnection after network timeout
```

---

## 6. Code Quality Rules

### 6.1 Before Writing Code
1. Read the relevant section in DESIGN.md
2. Check if similar code exists (don't duplicate)
3. Verify naming matches canonical names
4. Understand the data flow

### 6.2 Implementation Standards
- Match DESIGN.md signatures exactly
- Use type hints everywhere
- Handle errors explicitly - no silent failures
- Log appropriately (DEBUG/INFO/ERROR)
- No magic numbers - use named constants

### 6.3 Prohibited Patterns
- `print()` for logging (use proper logger)
- `# type: ignore` without explanation
- Swallowing exceptions silently
- Global mutable state
- Circular imports
- `from module import *`
- Placeholder/mock implementations
- Hardcoded values that should be config

---

## 7. Git Workflow

### 7.1 Commit Messages
Format: `<component>: <brief description>`

Examples:
- `server: implement SensorHub publish/subscribe`
- `android: fix camera permission handling`
- `docs: update setup guide`

### 7.2 Commit Rules
- Commit after each completed task (REQUIRED)
- Never commit broken code
- Never commit with failing tests
- Always run LSP diagnostics before committing

---

## 8. Communication Protocol

### 8.1 Status Updates
Report:
- What task you're on (TASKS.md reference)
- What you've completed
- Any blockers or questions
- What's next

### 8.2 Asking Questions
- Reference specific task: "Task 3.2 in server/TASKS.md"
- Describe what's unclear
- Propose options if you have them
- Wait for response before proceeding

### 8.3 Reporting Problems
- Expected vs actual behavior
- Error messages
- What you've tried
- Don't attempt multiple fixes without feedback

---

## 9. Component-Specific Rules

Each component's AGENTS.md may add rules that **extend** but cannot **override** these global rules.

If conflict exists, this document wins.

---

## 10. Rule Violations

If you violate a rule:
1. **STOP** immediately
2. **Report** the violation
3. **Wait** for guidance
4. **Don't** silently fix it

---

## 11. Anti-Patterns & Quality Gates

### 11.1 Implementation Anti-Patterns
- **Placeholder code**: Never `# TODO: implement` and move on
- **Mock implementations**: No fake code that pretends to work
- **Hardcoded workarounds**: No magic numbers as "temporary" fixes
- **Copy-paste blindly**: Don't copy code you can't explain
- **Over-abstraction**: Don't abstract until there's real need

### 11.2 Process Anti-Patterns
- **Parallel sprawl**: Don't start multiple tasks simultaneously
- **Silent pivots**: Don't change approach without announcing
- **Optimistic completion**: Don't mark done until verified
- **Doc procrastination**: Update docs as you go
- **Test skipping**: Don't skip tests to move faster

### 11.3 Quality Gates - Before Starting Phase
- [ ] Previous phase 100% complete
- [ ] All tests passing
- [ ] TASKS.md accurate
- [ ] No unresolved REVIEW items

### 11.4 Quality Gates - Before Component "Done"
- [ ] All TASKS.md items checked
- [ ] Integration tested
- [ ] DESIGN.md matches implementation
- [ ] No errors/warnings/debug output
- [ ] Performance within targets

---

## 12. Templates

### 12.1 Template: Root AGENTS.md

```markdown
# [Project Name]

> ⚠️ **AGENT NOTICE**: Read [AGENT_RULES.md](AGENT_RULES.md) first. Those rules are mandatory.

## Project Overview

[2-3 sentence description of what this project does]

### Key Principles

- [Principle 1]
- [Principle 2]
- [Principle 3]

## System Architecture

[ASCII diagram showing major components and data flow]

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│Component │────▶│Component │────▶│Component │
│    A     │     │    B     │     │    C     │
└──────────┘     └──────────┘     └──────────┘
```

## Directory Structure

```
project/
├── AGENT_RULES.md
├── AGENTS.md
├── ROADMAP.md
├── component-a/
│   ├── AGENTS.md
│   ├── DESIGN.md
│   └── TASKS.md
└── component-b/
    ├── AGENTS.md
    ├── DESIGN.md
    └── TASKS.md
```

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| component-a | [what it does] | [planning/active/done] |
| component-b | [what it does] | [planning/active/done] |

## Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| [layer] | [tech] | [why] |

## Canonical Names (Locked)

| Concept | Canonical Name | NOT |
|---------|---------------|-----|
| [concept] | `ExactName` | OtherName, AnotherName |

## Performance Targets

| Metric | Target |
|--------|--------|
| [metric] | [value] |

## Hardware/Environment

[List key hardware, deployment environment, etc.]

## Related Resources

- [Link to external docs]
- [Link to reference implementations]
```

### 12.2 Template: Component AGENTS.md

```markdown
# [Component Name] - Development Guide

> ⚠️ **AGENT NOTICE**: Read [../AGENT_RULES.md](../AGENT_RULES.md) first. Follow TASKS.md exactly.

## Overview

[2-3 sentences: what this component does, its role in the system]

## Architecture

[ASCII diagram of this component's internal structure]

```
┌────────────────────────────────────────┐
│            Component Name              │
├────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐           │
│  │ Module A │  │ Module B │           │
│  └────┬─────┘  └────┬─────┘           │
│       └──────┬──────┘                 │
│              ▼                        │
│       ┌──────────┐                    │
│       │ Module C │                    │
│       └──────────┘                    │
└────────────────────────────────────────┘
```

## Tech Stack

| Aspect | Choice | Notes |
|--------|--------|-------|
| Language | [lang] | [version] |
| Framework | [framework] | [why] |
| Key Libraries | [libs] | [purpose] |

## Key Classes/Modules

| Class | Purpose | Location |
|-------|---------|----------|
| `ClassName` | [what it does] | `path/to/file.py` |

## Data Flow

[Describe how data moves through this component]

## Configuration

[Key config options and where they live]

## File Structure

```
component/
├── AGENTS.md
├── DESIGN.md
├── TASKS.md
└── src/
    ├── module_a/
    └── module_b/
```

## Integration Points

| Connects To | Protocol | Data |
|-------------|----------|------|
| [component] | [WebSocket/REST/etc] | [what data] |

## Development Setup

[How to set up local dev environment]

## Testing

[How to run tests]

## Related Documents

- [DESIGN.md](DESIGN.md) - Technical specification
- [TASKS.md](TASKS.md) - Development tasks
- [../ROADMAP.md](../ROADMAP.md) - Project timeline
```

### 12.3 Template: DESIGN.md

```markdown
# [Component Name] - Design Document

## 1. Overview

[Paragraph describing the component's purpose and responsibilities]

## 2. Design Principles

1. **[Principle]** - [explanation]
2. **[Principle]** - [explanation]
3. **[Principle]** - [explanation]

## 3. Architecture

### 3.1 Component Diagram

[ASCII diagram]

### 3.2 Data Flow

[ASCII diagram or description]

## 4. Core Components

### 4.1 [ComponentName]

[Description of purpose]

```python
# Interface definition with types
class ComponentName:
    """
    [Docstring explaining purpose]
    """
    
    def __init__(self, config: ConfigType):
        """Initialize with configuration."""
        pass
    
    def method_name(self, param: ParamType) -> ReturnType:
        """
        [What this method does]
        
        Args:
            param: [description]
            
        Returns:
            [description]
        """
        pass
```

### 4.2 [NextComponent]

[Repeat pattern for each major component]

## 5. Data Models

### 5.1 [ModelName]

```python
@dataclass
class ModelName:
    field_one: str
    field_two: int
    field_three: Optional[float] = None
```

## 6. API / Interfaces

### 6.1 REST Endpoints (if applicable)

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| GET | /api/resource | - | `ResourceList` |
| POST | /api/resource | `CreateRequest` | `Resource` |

### 6.2 WebSocket Messages (if applicable)

**Client → Server:**
```json
{
  "type": "message_type",
  "data": {}
}
```

**Server → Client:**
```json
{
  "type": "response_type",
  "data": {}
}
```

## 7. Configuration

```yaml
# config.yaml
component:
  setting_one: value
  setting_two: value
  nested:
    setting: value
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| setting_one | string | "default" | [description] |

## 8. Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `ErrorName` | [when it occurs] | [how to handle] |

## 9. Performance Considerations

- [Performance consideration 1]
- [Performance consideration 2]
- [Optimization strategy]

## 10. Security Considerations

- [Security consideration if applicable]

## 11. Testing Strategy

### Unit Tests
- [What to unit test]

### Integration Tests
- [What to integration test]

## 12. Future Considerations

- [Potential future enhancement]
- [Known limitation to address later]
```

### 12.4 Template: TASKS.md

```markdown
# [Component Name] - Development Tasks

## Overview

[One sentence describing what completing these tasks achieves]

**Reference Documents:**
- [AGENTS.md](AGENTS.md) - Component overview
- [DESIGN.md](DESIGN.md) - Technical specification
- [../ROADMAP.md](../ROADMAP.md) - Project timeline

---

## Phase 0: Setup

### 0.1 Development Environment
- [ ] [Setup task 1]
- [ ] [Setup task 2]
- [ ] Verify build/run works

### 0.2 Project Structure
- [ ] Create directory structure per DESIGN.md
- [ ] Add configuration files
- [ ] Add .gitignore

---

## Phase 1: [Foundation/Core]

### 1.1 [First Module]
- [ ] Create `path/to/file.py`:
  - [Specific implementation detail]
  - [Another detail]
  - [Interface matches DESIGN.md §4.1]
- [ ] Add unit tests
- [ ] Verify integration

### 1.2 [Second Module]
- [ ] Create `path/to/another.py`:
  - [Detail]
  - [Detail]
- [ ] Add unit tests

---

## Phase 2: [Feature Area]

### 2.1 [Feature]
- [ ] Implement [feature]:
  - [Subtask]
  - [Subtask]
- [ ] Add tests
- [ ] Update config if needed

### 2.2 [Another Feature]
- [ ] [Task]
- [ ] [Task]

---

## Phase 3: [Integration]

### 3.1 [Integration Point]
- [ ] Connect to [other component]
- [ ] Handle errors gracefully
- [ ] Add integration tests

---

## Phase 4: [Testing & Polish]

### 4.1 Testing
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing complete

### 4.2 Documentation
- [ ] Code comments complete
- [ ] DESIGN.md matches implementation

### 4.3 Performance
- [ ] Meets performance targets from DESIGN.md
- [ ] No memory leaks
- [ ] No excessive logging

---

## Success Criteria

- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]
- [ ] All tests pass
- [ ] No lint errors/warnings
- [ ] Documentation complete

---

## Future Enhancements

<!-- Add ideas here instead of implementing them now -->
- [ ] [Future idea 1]
- [ ] [Future idea 2]

---

## Review Items

<!-- Edge cases and questions that need human input -->
- [ ] REVIEW: [Question or edge case needing decision]
```

---

## Summary Checklist

Before any action:
- [ ] Did I check for AGENTS.md/TASKS.md/DESIGN.md?
- [ ] Is this task in TASKS.md?
- [ ] Am I following naming conventions?
- [ ] Am I staying within scope?
- [ ] Should I ask before proceeding?
- [ ] Will I leave things clean?

---

*This file is designed to be dropped into any project root unchanged.*
*Customize project specifics in AGENTS.md, not here.*
