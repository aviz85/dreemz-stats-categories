import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  LinearProgress,
  Chip,
  Alert,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Speed as SpeedIcon,
  CheckCircle as SuccessIcon,
  Category as CategoryIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { dashboardApi } from '../utils/api';

const MetricCard = ({ title, value, subtitle, icon: Icon, color = 'primary' }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
        <Typography color="text.secondary" gutterBottom variant="subtitle2">
          {title}
        </Typography>
        <Icon color={color} />
      </Box>
      <Typography variant="h3" component="div" color={`${color}.main`}>
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {subtitle}
      </Typography>
    </CardContent>
  </Card>
);

const CategoryChart = ({ categories }) => (
  <Paper sx={{ p: 3, height: 400 }}>
    <Typography variant="h6" gutterBottom>
      Top Categories (All Primary + Secondary + Tertiary)
    </Typography>
    <ResponsiveContainer width="100%" height="90%">
      <BarChart data={categories.slice(0, 10)}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="name" 
          angle={-45}
          textAnchor="end"
          height={80}
          interval={0}
        />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#667eea" />
      </BarChart>
    </ResponsiveContainer>
  </Paper>
);

const RecentDreams = ({ recentDreams }) => (
  <Paper sx={{ p: 3 }}>
    <Typography variant="h6" gutterBottom>
      Recent Multi-Category Normalizations
    </Typography>
    <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
      {recentDreams.length > 0 ? (
        recentDreams.map((dream, index) => (
          <Box key={index} sx={{ py: 2, borderBottom: '1px solid #f0f0f0' }}>
            <Typography variant="body2" color="text.secondary">
              #{dream.id}: {dream.original}
            </Typography>
            <Typography variant="h6" sx={{ my: 1 }}>
              → {dream.normalized}
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {dream.categories.map((cat, catIndex) => {
                const chipColors = ['primary', 'secondary', 'success'];
                const chipLabels = ['Primary', 'Secondary', 'Tertiary'];
                return (
                  <Box key={catIndex} sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                      label={cat.category}
                      color={chipColors[catIndex] || 'default'}
                      size="small"
                      variant="filled"
                    />
                    <Chip
                      label={cat.subcategory}
                      variant="outlined"
                      size="small"
                    />
                    <Typography variant="caption" color="text.secondary">
                      ({chipLabels[catIndex]})
                    </Typography>
                  </Box>
                );
              })}
            </Box>
          </Box>
        ))
      ) : (
        <Alert severity="info">
          No dreams normalized yet. Start the V3 pipeline to see multi-category normalizations.
        </Alert>
      )}
    </Box>
  </Paper>
);

const LiveDashboard = ({ autoRefresh, refreshTrigger }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await dashboardApi.getStatus();
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [refreshTrigger]);

  const handleStart = async () => {
    try {
      await dashboardApi.startPipeline();
      fetchData(); // Refresh after starting
    } catch (err) {
      console.error('Failed to start pipeline:', err);
    }
  };

  const handleStop = async () => {
    try {
      await dashboardApi.stopPipeline();
      fetchData(); // Refresh after stopping
    } catch (err) {
      console.error('Failed to stop pipeline:', err);
    }
  };

  if (loading && !data) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading dashboard data: {error}
        <Button onClick={fetchData} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  const { status, database } = data || {};

  return (
    <Box>
      {/* Pipeline Controls */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Chip
            label={status?.is_running ? `Running (PID: ${status.pid})` : 'Stopped'}
            color={status?.is_running ? 'success' : 'error'}
            icon={status?.is_running ? <PlayIcon /> : <StopIcon />}
          />
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<PlayIcon />}
            onClick={handleStart}
            disabled={status?.is_running}
          >
            Start V3 Pipeline
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<StopIcon />}
            onClick={handleStop}
            disabled={!status?.is_running}
          >
            Stop Pipeline
          </Button>
        </Box>
      </Paper>

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Progress"
            value={`${(status?.percentage || 0).toFixed(1)}%`}
            subtitle={`${(status?.current || 0).toLocaleString()} / ${(status?.total || 0).toLocaleString()}`}
            icon={LinearProgress}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Processing Rate"
            value={status?.dreams_per_minute || 0}
            subtitle="dreams per minute"
            icon={SpeedIcon}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Success Rate"
            value={`${(status?.success_rate || 0).toFixed(1)}%`}
            subtitle={`${status?.failed_count || 0} failed`}
            icon={SuccessIcon}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Multi-Category"
            value={`${(status?.multi_category_percentage || 0).toFixed(1)}%`}
            subtitle="dreams with 2+ categories"
            icon={CategoryIcon}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Time Remaining"
            value={status?.remaining_hours ? `${Math.floor(status.remaining_hours)}h ${Math.floor((status.remaining_hours % 1) * 60)}m` : '--'}
            subtitle={status?.eta ? `ETA: ${status.eta}` : 'ETA: --'}
            icon={TimeIcon}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Progress Bar */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Overall Progress
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ width: '100%', mr: 1 }}>
            <LinearProgress
              variant="determinate"
              value={status?.percentage || 0}
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>
          <Box sx={{ minWidth: 35 }}>
            <Typography variant="body2" color="text.secondary">
              {`${Math.round(status?.percentage || 0)}%`}
            </Typography>
          </Box>
        </Box>
        
        {/* Multi-Category Stats */}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.light', borderRadius: 2 }}>
              <Typography variant="h4" color="primary.contrastText">
                {(database?.single_category || 0).toLocaleString()}
              </Typography>
              <Typography variant="caption" color="primary.contrastText">
                Single Category
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'secondary.light', borderRadius: 2 }}>
              <Typography variant="h4" color="secondary.contrastText">
                {(database?.double_category || 0).toLocaleString()}
              </Typography>
              <Typography variant="caption" color="secondary.contrastText">
                Two Categories
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.light', borderRadius: 2 }}>
              <Typography variant="h4" color="success.contrastText">
                {(database?.triple_category || 0).toLocaleString()}
              </Typography>
              <Typography variant="caption" color="success.contrastText">
                Three Categories
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Charts and Recent Data */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <CategoryChart categories={database?.categories || []} />
        </Grid>
        <Grid item xs={12} md={5}>
          <RecentDreams recentDreams={database?.recent || []} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default LiveDashboard;