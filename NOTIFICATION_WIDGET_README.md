# Notification Widget Feature

## Overview
A persistent notification widget that displays in the bottom-right corner of the application, showing active inference jobs with live progress updates and completed job previews with thumbnail images.

## Components Created

### 1. NotificationContext (`frontend/src/contexts/NotificationContext.jsx`)
- React Context provider for managing notification state
- Polls QueueService every 3 seconds for job updates
- Tracks active jobs (pending/processing) and completed jobs
- Auto-expands widget when jobs complete
- Persists state in localStorage to survive page refreshes
- Manages dismissal actions

**Key Functions:**
- `addTrackedJob(jobData)` - Add a job to track
- `dismissJob(jobId)` - Dismiss a completed job
- `dismissAll()` - Clear all completed jobs
- `refreshJobs()` - Manually refresh job list

### 2. NotificationWidget (`frontend/src/components/NotificationWidget.jsx`)
- Persistent UI component in bottom-right corner
- Displays active jobs with progress bars and loading animations
- Shows completed jobs with thumbnails (when available)
- Expandable/collapsible behavior
- Shows job counts and status badges
- Individual dismiss buttons and "Clear All" action

**Features:**
- Auto-hides when no jobs are active or completed
- Shows progress percentage for active jobs
- Displays thumbnail previews for completed jobs
- Compact collapsed view with job counts
- Smooth animations and transitions

## Integration Points

### Modified Files

#### `frontend/src/App.js`
- Wrapped application in `NotificationProvider`
- Added `NotificationWidget` component to render tree
- Widget persists across all routes

#### `frontend/src/components/GenerationDialog.jsx`
- Integrated `useNotifications` hook
- Calls `addTrackedJob()` after job submission
- Dialog can now be closed immediately after submission
- Jobs tracked and shown in notification widget

#### `frontend/src/components/EnhancedGenerationDialog.jsx`
- Integrated `useNotifications` hook
- Calls `addTrackedJob()` after job submission
- Supports both ComfyUI and OpenAI Sora workflows
- Dialog can now be closed immediately after submission

#### `frontend/src/components/BatchGenerationDialog.jsx`
- Integrated `useNotifications` hook
- Tracks all jobs from batch generation
- Each job in batch shown separately in widget

#### `frontend/src/services/queueService.js`
- Added `getJob(jobId)` method for individual job retrieval

## User Flow

1. User opens generation dialog (image or video)
2. User configures parameters and submits job
3. Dialog closes immediately (non-blocking)
4. Notification widget appears in bottom-right corner showing job progress
5. Widget polls every 3 seconds for status updates
6. Progress bar updates in real-time
7. When job completes:
   - Widget auto-expands
   - Toast notification appears
   - Thumbnail preview shown (if available)
8. User can dismiss individual jobs or clear all
9. Dismissed jobs persist across page refreshes via localStorage

## State Management

### LocalStorage Structure
```json
{
  "completedJobs": [
    {
      "id": "job-uuid",
      "generation_type": "image",
      "status": "completed",
      "result": {
        "url": "/uploads/...",
        "thumbnail_url": "/uploads/...",
        "seed": 123456
      },
      "params": {
        "prompt": "..."
      }
    }
  ],
  "dismissedJobs": ["job-uuid-1", "job-uuid-2"],
  "timestamp": 1234567890
}
```

### Context State
- `activeJobs` - Array of pending/processing jobs
- `completedJobs` - Array of completed jobs not yet dismissed
- `dismissedJobs` - Set of dismissed job IDs
- `isExpanded` - Widget expanded state
- `isPolling` - Polling active state

## Styling

The widget uses Shadcn UI components with consistent theming:
- Glass-panel effect with border
- Indigo accent colors for active states
- Green indicators for completed jobs
- Smooth hover transitions
- Responsive layout with max height scrolling

## Technical Details

### Polling Strategy
- Interval: 3000ms (3 seconds)
- Fetches jobs with status: `processing,pending,completed`
- Limit: 50 jobs per request
- Automatically detects newly completed jobs
- Triggers toast notifications for completions

### Performance Considerations
- Polls only when component is mounted
- Uses `useCallback` to prevent unnecessary re-renders
- Filters out dismissed jobs from storage
- Limits displayed items with scrolling

### Error Handling
- Silently logs polling errors to console
- Does not disrupt user experience on API failures
- Continues polling even if requests fail
- LocalStorage errors caught and logged

## Future Enhancements

Potential improvements:
- Click on completed job to view in gallery
- Retry failed jobs from widget
- Cancel active jobs from widget
- Sound notification on completion
- Desktop notifications (browser API)
- Job grouping by project/clip
- Export job results directly from widget
- Estimated time remaining for active jobs
