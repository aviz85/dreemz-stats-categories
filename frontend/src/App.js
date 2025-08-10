import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Paper,
  Alert
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Import components
import Dashboard from './components/Dashboard';
import UniqueDreams from './components/UniqueDreams';
import Categories from './components/Categories';
import Subcategories from './components/Subcategories';
import DreamDetails from './components/DreamDetails';
import DataImport from './components/DataImport';

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    background: {
      default: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
  },
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [error, setError] = useState(null);
  const [dbStats, setDbStats] = useState(null);

  // Fetch database stats on app load
  useEffect(() => {
    fetchDatabaseStats();
  }, []);

  const fetchDatabaseStats = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setDbStats(data.database);
    } catch (err) {
      console.error('Error fetching database stats:', err);
      setError('Failed to load database statistics: ' + err.message);
    }
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    setError(null); // Clear errors when switching tabs
  };

  const tabs = [
    { label: '📊 Dashboard', component: <Dashboard dbStats={dbStats} /> },
    { label: '🔍 Unique Dreams', component: <UniqueDreams /> },
    { label: '📊 Categories', component: <Categories /> },
    { label: '🎯 Subcategories', component: <Subcategories /> },
    { label: '🔍 Dream Details', component: <DreamDetails /> },
    { label: '📥 Import Data', component: <DataImport /> },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}>
        <AppBar position="sticky" sx={{ backgroundColor: 'rgba(255,255,255,0.95)', color: '#333' }}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#333' }}>
              🎯 Dream Analytics Dashboard
            </Typography>
          </Toolbar>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ backgroundColor: 'white', color: '#333' }}
          >
            {tabs.map((tab, index) => (
              <Tab key={index} label={tab.label} />
            ))}
          </Tabs>
        </AppBar>

        <Container maxWidth="xl">
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {tabs.map((tab, index) => (
            <TabPanel key={index} value={currentTab} index={index}>
              {tab.component}
            </TabPanel>
          ))}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;