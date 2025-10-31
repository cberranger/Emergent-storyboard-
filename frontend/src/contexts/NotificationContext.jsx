import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { queueService } from '@/services';
import { toast } from 'sonner';

const NotificationContext = createContext();

const STORAGE_KEY = 'storycanvas_notifications';
const POLL_INTERVAL = 3000;

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [activeJobs, setActiveJobs] = useState([]);
  const [completedJobs, setCompletedJobs] = useState([]);
  const [dismissedJobs, setDismissedJobs] = useState(new Set());
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    loadFromStorage();
    startPolling();
    
    return () => {
      stopPolling();
    };
  }, []);

  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        setDismissedJobs(new Set(data.dismissedJobs || []));
        if (data.completedJobs) {
          setCompletedJobs(data.completedJobs.filter(job => 
            !data.dismissedJobs?.includes(job.id)
          ));
        }
      }
    } catch (error) {
      console.error('Error loading notification state:', error);
    }
  };

  const saveToStorage = (completed, dismissed) => {
    try {
      const data = {
        completedJobs: completed,
        dismissedJobs: Array.from(dismissed),
        timestamp: Date.now()
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving notification state:', error);
    }
  };

  const pollJobs = useCallback(async () => {
    try {
      const data = await queueService.getJobs({
        status: 'processing,pending,completed',
        limit: 50
      });

      const jobs = data.jobs || [];
      const active = jobs.filter(job => 
        job.status === 'processing' || job.status === 'pending'
      );
      const newCompleted = jobs.filter(job => 
        job.status === 'completed' && !dismissedJobs.has(job.id)
      );

      setActiveJobs(active);

      const previousCompletedIds = new Set(completedJobs.map(j => j.id));
      const justCompleted = newCompleted.filter(job => !previousCompletedIds.has(job.id));
      
      if (justCompleted.length > 0) {
        setIsExpanded(true);
        justCompleted.forEach(job => {
          toast.success(`Job completed: ${job.generation_type} generation`);
        });
      }

      const updatedCompleted = [
        ...completedJobs.filter(job => !dismissedJobs.has(job.id)),
        ...justCompleted
      ];
      
      setCompletedJobs(updatedCompleted);
      saveToStorage(updatedCompleted, dismissedJobs);
      
    } catch (error) {
      console.error('Error polling jobs:', error);
    }
  }, [dismissedJobs, completedJobs]);

  const startPolling = () => {
    setIsPolling(true);
  };

  const stopPolling = () => {
    setIsPolling(false);
  };

  useEffect(() => {
    let intervalId;
    if (isPolling) {
      pollJobs();
      intervalId = setInterval(pollJobs, POLL_INTERVAL);
    }
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isPolling, pollJobs]);

  const dismissJob = (jobId) => {
    const newDismissed = new Set(dismissedJobs);
    newDismissed.add(jobId);
    setDismissedJobs(newDismissed);
    
    const updatedCompleted = completedJobs.filter(job => job.id !== jobId);
    setCompletedJobs(updatedCompleted);
    saveToStorage(updatedCompleted, newDismissed);
  };

  const dismissAll = () => {
    const allIds = completedJobs.map(job => job.id);
    const newDismissed = new Set([...dismissedJobs, ...allIds]);
    setDismissedJobs(newDismissed);
    setCompletedJobs([]);
    saveToStorage([], newDismissed);
  };

  const clearDismissed = () => {
    setDismissedJobs(new Set());
    saveToStorage(completedJobs, new Set());
  };

  const addTrackedJob = (jobData) => {
    setActiveJobs(prev => {
      const exists = prev.some(j => j.id === jobData.id);
      if (exists) return prev;
      return [...prev, jobData];
    });
  };

  const value = {
    activeJobs,
    completedJobs,
    dismissedJobs,
    isExpanded,
    setIsExpanded,
    dismissJob,
    dismissAll,
    clearDismissed,
    addTrackedJob,
    refreshJobs: pollJobs
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
