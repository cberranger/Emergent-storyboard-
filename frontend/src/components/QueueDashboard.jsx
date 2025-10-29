import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  RefreshCw,
  Play,
  Pause,
  Square,
  Trash2,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  Filter,
  Download
} from 'lucide-react';
import { API } from '@/config';
import axios from 'axios';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import QueueJobCard from './QueueJobCard';

const QueueDashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0,
    cancelled: 0
  });

  useEffect(() => {
    fetchJobs();
    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
      fetchJobs();
    }, 5000);
    setRefreshInterval(interval);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [statusFilter]);

  const fetchJobs = async () => {
    try {
      const params = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      const response = await axios.get(`${API}/v1/queue/jobs`, { params });
      const jobData = Array.isArray(response.data) ? response.data : (response.data.jobs || []);
      setJobs(jobData);
      calculateStats(jobData);
    } catch (error) {
      console.error('Error fetching queue jobs:', error);
      toast.error('Failed to fetch queue jobs');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (jobList) => {
    const stats = {
      total: jobList.length,
      pending: 0,
      processing: 0,
      completed: 0,
      failed: 0,
      cancelled: 0
    };

    jobList.forEach(job => {
      const status = job.status?.toLowerCase();
      if (status === 'pending' || status === 'queued') stats.pending++;
      else if (status === 'processing') stats.processing++;
      else if (status === 'completed') stats.completed++;
      else if (status === 'failed') stats.failed++;
      else if (status === 'cancelled') stats.cancelled++;
    });

    setStats(stats);
  };

  const handleRetryJob = async (jobId) => {
    try {
      await axios.post(`${API}/v1/queue/jobs/${jobId}/retry`);
      toast.success('Job retry initiated');
      fetchJobs();
    } catch (error) {
      console.error('Error retrying job:', error);
      toast.error('Failed to retry job');
    }
  };

  const handleCancelJob = async (jobId) => {
    try {
      await axios.post(`${API}/v1/queue/jobs/${jobId}/cancel`);
      toast.success('Job cancelled');
      fetchJobs();
    } catch (error) {
      console.error('Error cancelling job:', error);
      toast.error('Failed to cancel job');
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job?')) return;

    try {
      await axios.delete(`${API}/v1/queue/jobs/${jobId}`);
      toast.success('Job deleted');
      fetchJobs();
    } catch (error) {
      console.error('Error deleting job:', error);
      toast.error('Failed to delete job');
    }
  };

  const handleClearCompleted = async () => {
    if (!window.confirm('Clear all completed jobs?')) return;

    try {
      await axios.delete(`${API}/v1/queue/clear`, {
        params: { status: 'completed' }
      });
      toast.success('Completed jobs cleared');
      fetchJobs();
    } catch (error) {
      console.error('Error clearing completed jobs:', error);
      toast.error('Failed to clear completed jobs');
    }
  };

  const handleClearFailed = async () => {
    if (!window.confirm('Clear all failed jobs?')) return;

    try {
      await axios.delete(`${API}/v1/queue/clear`, {
        params: { status: 'failed' }
      });
      toast.success('Failed jobs cleared');
      fetchJobs();
    } catch (error) {
      console.error('Error clearing failed jobs:', error);
      toast.error('Failed to clear failed jobs');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'failed':
        return <XCircle className="w-4 h-4" />;
      case 'cancelled':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500';
      case 'processing':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'cancelled':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-6 bg-gray-900">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-primary">Queue Dashboard</h1>
            <p className="text-sm text-secondary">Monitor generation pipeline and job progress</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchJobs}
              className="border-panel hover:bg-panel-dark"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <Card className="bg-panel border-panel">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-primary">{stats.total}</div>
              <div className="text-xs text-secondary">Total Jobs</div>
            </CardContent>
          </Card>

          <Card className="bg-panel border-panel">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-yellow-500" />
                <div className="text-2xl font-bold text-primary">{stats.pending}</div>
              </div>
              <div className="text-xs text-secondary">Pending</div>
            </CardContent>
          </Card>

          <Card className="bg-panel border-panel">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                <div className="text-2xl font-bold text-primary">{stats.processing}</div>
              </div>
              <div className="text-xs text-secondary">Processing</div>
            </CardContent>
          </Card>

          <Card className="bg-panel border-panel">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <div className="text-2xl font-bold text-primary">{stats.completed}</div>
              </div>
              <div className="text-xs text-secondary">Completed</div>
            </CardContent>
          </Card>

          <Card className="bg-panel border-panel">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <XCircle className="w-4 h-4 text-red-500" />
                <div className="text-2xl font-bold text-primary">{stats.failed}</div>
              </div>
              <div className="text-xs text-secondary">Failed</div>
            </CardContent>
          </Card>

          <Card className="bg-panel border-panel">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-gray-500" />
                <div className="text-2xl font-bold text-primary">{stats.cancelled}</div>
              </div>
              <div className="text-xs text-secondary">Cancelled</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Actions */}
        <Card className="bg-panel border-panel">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4 text-secondary" />
                  <span className="text-sm text-secondary">Filter by status:</span>
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Jobs</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="processing">Processing</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearCompleted}
                  disabled={stats.completed === 0}
                  className="border-panel hover:bg-panel-dark"
                >
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  Clear Completed
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearFailed}
                  disabled={stats.failed === 0}
                  className="border-panel hover:bg-panel-dark"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  Clear Failed
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Jobs List */}
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <Card className="bg-panel border-panel">
              <CardContent className="p-8 text-center">
                <div className="text-secondary">No jobs found</div>
              </CardContent>
            </Card>
          ) : (
            jobs.map((job) => (
              <QueueJobCard
                key={job.id}
                job={job}
                onRetry={handleRetryJob}
                onCancel={handleCancelJob}
                onDelete={handleDeleteJob}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default QueueDashboard;
