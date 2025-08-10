import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  AlertTitle,
  CircularProgress,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Paper,
  Grid
} from '@mui/material';
import {
  CloudUpload as ImportIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

const DataImport = () => {
  const [importStatus, setImportStatus] = useState(null);
  const [isImporting, setIsImporting] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [existingCount, setExistingCount] = useState(0);
  const [dbStats, setDbStats] = useState(null);

  // Poll for status updates
  useEffect(() => {
    let interval;
    
    if (isImporting) {
      interval = setInterval(fetchImportStatus, 1000); // Poll every second
    }
    
    // Initial status check
    fetchImportStatus();
    fetchDatabaseStats();
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isImporting]);

  const fetchImportStatus = async () => {
    try {
      const response = await fetch('/api/import/status');
      const data = await response.json();
      setImportStatus(data);
      
      // Stop polling if import is complete
      if (data && !data.running && (data.success !== null)) {
        setIsImporting(false);
        fetchDatabaseStats(); // Refresh stats after import
      }
    } catch (error) {
      console.error('Error fetching import status:', error);
    }
  };

  const fetchDatabaseStats = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setDbStats(data.database);
    } catch (error) {
      console.error('Error fetching database stats:', error);
    }
  };

  const startImport = async (force = false) => {
    try {
      const response = await fetch('/api/import/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setIsImporting(true);
        setShowConfirmDialog(false);
        fetchImportStatus();
      } else {
        if (data.existing_count && !force) {
          setExistingCount(data.existing_count);
          setShowConfirmDialog(true);
        } else {
          alert(data.message || 'Failed to start import');
        }
      }
    } catch (error) {
      console.error('Error starting import:', error);
      alert('Failed to start import');
    }
  };

  const getProgressPercentage = () => {
    if (!importStatus || importStatus.total === 0) return 0;
    return Math.round((importStatus.progress / importStatus.total) * 100);
  };

  const getStatusIcon = () => {
    if (!importStatus) return null;
    
    if (importStatus.running) {
      return <CircularProgress size={24} />;
    }
    
    if (importStatus.success === true) {
      return <SuccessIcon color="success" />;
    }
    
    if (importStatus.success === false) {
      return <ErrorIcon color="error" />;
    }
    
    return <ImportIcon />;
  };

  const getStatusColor = () => {
    if (!importStatus) return 'default';
    if (importStatus.running) return 'primary';
    if (importStatus.success === true) return 'success';
    if (importStatus.success === false) return 'error';
    return 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Data Import Manager
      </Typography>

      {/* Database Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {dbStats?.total_dreams?.toLocaleString() || '0'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Dreams
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {dbStats?.unique_titles?.toLocaleString() || '0'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Unique Titles
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {dbStats?.categories || '0'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Categories
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {dbStats?.subcategories || '0'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Subcategories
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Import Card */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ mr: 2 }}>
              {getStatusIcon()}
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6">
                CSV Data Import
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Import dreams_export.csv (115,624 dreams)
              </Typography>
            </Box>
            <Box>
              <Chip 
                label={importStatus?.running ? 'RUNNING' : importStatus?.success === true ? 'COMPLETED' : importStatus?.success === false ? 'FAILED' : 'READY'}
                color={getStatusColor()}
                size="small"
              />
            </Box>
          </Box>

          {/* Status Message */}
          {importStatus && (
            <Alert 
              severity={
                importStatus.running ? 'info' : 
                importStatus.success === true ? 'success' : 
                importStatus.success === false ? 'error' : 
                'info'
              }
              sx={{ mb: 2 }}
            >
              <AlertTitle>
                {importStatus.running ? 'Import in Progress' : 
                 importStatus.success === true ? 'Import Successful' : 
                 importStatus.success === false ? 'Import Failed' : 
                 'Ready to Import'}
              </AlertTitle>
              {importStatus.message}
              {importStatus.error && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Error: {importStatus.error}
                </Typography>
              )}
            </Alert>
          )}

          {/* Progress Bar */}
          {importStatus?.running && (
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="textSecondary">
                  Progress: {importStatus.progress?.toLocaleString()} / {importStatus.total?.toLocaleString()} dreams
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {getProgressPercentage()}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={getProgressPercentage()} 
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
          )}

          {/* Import Statistics */}
          {importStatus?.success === true && importStatus.progress > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1" gutterBottom>
                Import Statistics:
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip label={`${importStatus.progress?.toLocaleString()} dreams imported`} color="success" variant="outlined" />
                <Chip label={`Last updated: ${new Date(importStatus.last_update).toLocaleTimeString()}`} variant="outlined" />
              </Box>
            </Box>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<ImportIcon />}
              onClick={() => startImport(false)}
              disabled={isImporting}
            >
              {isImporting ? 'Importing...' : 'Start Import'}
            </Button>
            
            {importStatus?.success === true && (
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => window.location.reload()}
              >
                Refresh Dashboard
              </Button>
            )}
          </Box>

          {/* Help Text */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="textSecondary">
              <strong>Note:</strong> This will import the dreams_export.csv file that was deployed with the application.
              The import process takes approximately 2-3 minutes for 115,624 dreams.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog
        open={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <WarningIcon color="warning" sx={{ mr: 1 }} />
            Database Already Contains Data
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            The database already contains {existingCount?.toLocaleString()} dreams. 
            Starting a new import will delete all existing data and replace it with the CSV data.
            <br /><br />
            Are you sure you want to continue?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={() => startImport(true)} 
            color="warning"
            variant="contained"
          >
            Yes, Replace All Data
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataImport;