import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Tabs,
  Tab,
  Box,
  Typography,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Search as SearchIcon,
  Category as CategoryIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import LiveDashboard from './components/LiveDashboard';
import UniqueDreams from './components/UniqueDreams';
import SimilaritySearch from './components/SimilaritySearch';
import CategoriesAnalysis from './components/CategoriesAnalysis';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [countdown, setCountdown] = useState(10);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Auto-refresh countdown for live dashboard
  useEffect(() => {
    if (activeTab === 0 && autoRefresh) {
      const interval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            setLastUpdate(new Date());
            return 10; // Reset countdown
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [activeTab, autoRefresh]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    if (!autoRefresh) {
      setCountdown(10);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Paper
        elevation={3}
        sx={{
          p: 3,
          mb: 3,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <div>
            <Typography variant="h3" component="h1" gutterBottom>
              🌙 Dream Normalizer V3 Dashboard
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Multi-Category Support: 1-3 categories per dream
            </Typography>
          </div>
          
          <Box display="flex" alignItems="center" gap={2}>
            {activeTab === 0 && (
              <Box display="flex" alignItems="center" gap={1}>
                <Chip
                  label={`Auto-refresh in ${countdown}s`}
                  variant={autoRefresh ? "filled" : "outlined"}
                  color="primary"
                  size="small"
                />
                <IconButton onClick={toggleAutoRefresh} size="small">
                  <RefreshIcon />
                </IconButton>
              </Box>
            )}
            {lastUpdate && (
              <Typography variant="caption" color="text.secondary">
                Last update: {lastUpdate.toLocaleTimeString()}
              </Typography>
            )}
          </Box>
        </Box>

        {/* Tabs Navigation */}
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 60,
              textTransform: 'none',
              fontSize: '1rem',
              fontWeight: 600,
            },
          }}
        >
          <Tab
            icon={<DashboardIcon />}
            label="Live Dashboard"
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            icon={<AnalyticsIcon />}
            label="Unique Dreams Analysis"
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            icon={<CategoryIcon />}
            label="Categories Analysis"
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            icon={<SearchIcon />}
            label="Similarity Search & Merge"
            iconPosition="start"
            sx={{ gap: 1 }}
          />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      <TabPanel value={activeTab} index={0}>
        <LiveDashboard
          autoRefresh={autoRefresh}
          refreshTrigger={countdown === 10 ? Date.now() : null}
        />
      </TabPanel>
      
      <TabPanel value={activeTab} index={1}>
        <UniqueDreams />
      </TabPanel>
      
      <TabPanel value={activeTab} index={2}>
        <CategoriesAnalysis />
      </TabPanel>
      
      <TabPanel value={activeTab} index={3}>
        <SimilaritySearch />
      </TabPanel>
    </Container>
  );
}

export default App;