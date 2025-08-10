import React, { useState, useEffect } from 'react';
import {
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Checkbox,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Autocomplete,
  Divider,
  IconButton,
  Tooltip,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Pagination,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import {
  Search as SearchIcon,
  Merge as MergeIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon
} from '@mui/icons-material';

const SimilaritySearch = () => {
  const [titles, setTitles] = useState([]);
  const [selectedTitle, setSelectedTitle] = useState(null);
  const [similarTitles, setSimilarTitles] = useState([]);
  const [selectedForMerge, setSelectedForMerge] = useState([]);
  const [loading, setLoading] = useState(false);
  const [merging, setMerging] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [searchCount, setSearchCount] = useState(10);
  const [unlimitedResults, setUnlimitedResults] = useState(false);
  const [similarityThreshold, setSimilarityThreshold] = useState(70);
  const [indexStatus, setIndexStatus] = useState('checking');
  const [sortBy, setSortBy] = useState('similarity'); // 'similarity' or 'count'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' or 'desc'
  const [refreshingIndex, setRefreshingIndex] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(25);

  // Load all titles on mount
  useEffect(() => {
    loadTitles();
    checkIndexStatus();
  }, []);

  const checkIndexStatus = async () => {
    try {
      // Try a test search to see if index is ready
      const response = await fetch('/api/similarity-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'test', k: 1 })
      });
      
      if (response.status === 503) {
        setIndexStatus('not_ready');
      } else {
        setIndexStatus('ready');
      }
    } catch (error) {
      setIndexStatus('error');
    }
  };

  const loadTitles = async () => {
    try {
      const response = await fetch('/api/all-titles');
      const data = await response.json();
      setTitles(data.titles);
    } catch (error) {
      setError('Failed to load titles');
    }
  };

  const searchSimilar = async () => {
    if (!selectedTitle) {
      setError('Please select a title first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setSimilarTitles([]);
    setSelectedForMerge([]);

    try {
      const response = await fetch('/api/similarity-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: selectedTitle.title,
          k: unlimitedResults ? 1000 : searchCount, // Use high number for unlimited
          threshold: similarityThreshold
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Search failed');
      }

      const data = await response.json();
      setSimilarTitles(data.similar);
      setCurrentPage(1); // Reset to first page on new search
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMerge = async () => {
    if (selectedForMerge.length === 0) {
      setError('Please select titles to merge');
      return;
    }

    const confirmMsg = `Merge ${selectedForMerge.length} title(s) into "${selectedTitle.title}"?\n\n` +
      `This will combine:\n` +
      `- ${selectedTitle.title} (${selectedTitle.count} dreams)\n` +
      selectedForMerge.map(t => `- ${t.title} (${t.count} dreams)`).join('\n') +
      `\n\nTotal after merge: ${selectedTitle.count + selectedForMerge.reduce((sum, t) => sum + t.count, 0)} dreams`;

    if (!window.confirm(confirmMsg)) {
      return;
    }

    setMerging(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/merge-titles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: selectedTitle.title,
          titles: selectedForMerge.map(t => t.title)
        })
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`Successfully merged ${data.merged_count} dreams. New total for "${data.target}": ${data.new_total_count} dreams`);
        
        // Update the selected title count
        setSelectedTitle({ ...selectedTitle, count: data.new_total_count });
        
        // Clear selections and refresh search results
        setSelectedForMerge([]);
        
        // Re-run the search to get updated results
        await searchSimilar();
        
        // Reload titles to get updated counts
        await loadTitles();
      } else {
        throw new Error(data.error || 'Merge failed');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setMerging(false);
    }
  };

  const toggleSelection = (title) => {
    const isSelected = selectedForMerge.find(t => t.title === title.title);
    if (isSelected) {
      setSelectedForMerge(selectedForMerge.filter(t => t.title !== title.title));
    } else {
      setSelectedForMerge([...selectedForMerge, title]);
    }
  };

  const getSortedTitles = () => {
    const sorted = [...similarTitles];
    if (sortBy === 'count') {
      return sorted.sort((a, b) => 
        sortOrder === 'desc' ? b.count - a.count : a.count - b.count
      );
    } else {
      return sorted.sort((a, b) => 
        sortOrder === 'desc' ? b.similarity - a.similarity : a.similarity - b.similarity
      );
    }
  };

  const getPaginatedTitles = () => {
    const sorted = getSortedTitles();
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sorted.slice(startIndex, startIndex + itemsPerPage);
  };

  const getTotalPages = () => {
    return Math.ceil(similarTitles.length / itemsPerPage);
  };

  const getSimilarityColor = (similarity) => {
    if (similarity >= 90) return '#4caf50';
    if (similarity >= 80) return '#8bc34a';
    if (similarity >= 70) return '#ffc107';
    if (similarity >= 60) return '#ff9800';
    return '#f44336';
  };

  const refreshIndex = async () => {
    setRefreshingIndex(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/refresh-index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`Index refreshed: ${data.total_titles} unique titles loaded`);
        // Re-run search if we have a selected title
        if (selectedTitle) {
          await searchSimilar();
        }
      } else {
        throw new Error(data.error || 'Failed to refresh index');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setRefreshingIndex(false);
    }
  };

  if (indexStatus === 'not_ready') {
    return (
      <Paper elevation={3} sx={{ p: 3, m: 2 }}>
        <Alert severity="warning">
          <Typography variant="h6">FAISS Index Not Ready</Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            The similarity search index is still being created. This process may take several minutes.
            Please wait for the embeddings to be generated...
          </Typography>
          <LinearProgress sx={{ mt: 2 }} />
        </Alert>
      </Paper>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={3}>
        {/* Search Section */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              <SearchIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Dream Title Similarity Search & Merge
            </Typography>
            
            <Grid container spacing={2} sx={{ mt: 2 }}>
              {/* Threshold Control */}
              <Grid item xs={12}>
                <Box sx={{ px: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Similarity Threshold: {similarityThreshold}%
                  </Typography>
                  <Slider
                    value={similarityThreshold}
                    onChange={(e, newValue) => setSimilarityThreshold(newValue)}
                    min={0}
                    max={100}
                    step={1}
                    marks={[
                      { value: 0, label: '0%' },
                      { value: 25, label: '25%' },
                      { value: 50, label: '50%' },
                      { value: 75, label: '75%' },
                      { value: 100, label: '100%' }
                    ]}
                    sx={{ width: '100%' }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  options={titles}
                  getOptionLabel={(option) => `${option.title} (${option.count} dreams)`}
                  value={selectedTitle}
                  onChange={(event, newValue) => {
                    setSelectedTitle(newValue);
                    setSimilarTitles([]);
                    setSelectedForMerge([]);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Select a dream title"
                      variant="outlined"
                      fullWidth
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TextField
                    label="Number of results"
                    type="number"
                    value={searchCount}
                    onChange={(e) => setSearchCount(Math.min(50, Math.max(5, parseInt(e.target.value) || 10)))}
                    fullWidth
                    inputProps={{ min: 5, max: 50 }}
                    disabled={unlimitedResults}
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={unlimitedResults}
                        onChange={(e) => setUnlimitedResults(e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Unlimited"
                    sx={{ whiteSpace: 'nowrap' }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={searchSimilar}
                  disabled={!selectedTitle || loading}
                  fullWidth
                  sx={{ height: '56px' }}
                  startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                >
                  {loading ? 'Searching...' : 'Search Similar'}
                </Button>
              </Grid>
            </Grid>

            {selectedTitle && (
              <Box sx={{ mt: 2 }}>
                <Chip
                  label={`Selected: ${selectedTitle.title} (${selectedTitle.count} dreams)`}
                  color="primary"
                  icon={<CheckCircleIcon />}
                />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Results Section */}
        {similarTitles.length > 0 && (
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
                <Typography variant="h6">
                  {similarTitles.length} dream titles found
                  {unlimitedResults && ` (threshold: ${similarityThreshold}%)`}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel>Sort by</InputLabel>
                    <Select
                      value={sortBy}
                      label="Sort by"
                      onChange={(e) => setSortBy(e.target.value)}
                    >
                      <MenuItem value="similarity">Similarity %</MenuItem>
                      <MenuItem value="count">Dream Count</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <ToggleButtonGroup
                    value={sortOrder}
                    exclusive
                    onChange={(e, newOrder) => newOrder && setSortOrder(newOrder)}
                    size="small"
                  >
                    <ToggleButton value="desc" aria-label="descending">
                      <ArrowDownwardIcon fontSize="small" />
                      Desc
                    </ToggleButton>
                    <ToggleButton value="asc" aria-label="ascending">
                      <ArrowUpwardIcon fontSize="small" />
                      Asc
                    </ToggleButton>
                  </ToggleButtonGroup>
                  
                  <Tooltip title="Refresh search index after merging">
                    <Button
                      variant="outlined"
                      onClick={refreshIndex}
                      disabled={refreshingIndex}
                      startIcon={refreshingIndex ? <CircularProgress size={20} /> : <RefreshIcon />}
                    >
                      {refreshingIndex ? 'Refreshing...' : 'Refresh Index'}
                    </Button>
                  </Tooltip>
                  
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleMerge}
                    disabled={selectedForMerge.length === 0 || merging}
                    startIcon={merging ? <CircularProgress size={20} /> : <MergeIcon />}
                  >
                    Merge Selected ({selectedForMerge.length})
                  </Button>
                </Box>
              </Box>

              <Divider sx={{ mb: 2 }} />

              <List>
                {getPaginatedTitles().map((item, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      mb: 1,
                      '&:hover': { backgroundColor: '#f5f5f5' }
                    }}
                  >
                    <Checkbox
                      checked={selectedForMerge.find(t => t.title === item.title) !== undefined}
                      onChange={() => toggleSelection(item)}
                    />
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body1">
                            {item.title}
                          </Typography>
                          <Chip
                            label={`${item.similarity}%`}
                            size="small"
                            sx={{
                              backgroundColor: getSimilarityColor(item.similarity),
                              color: 'white'
                            }}
                          />
                          <Chip
                            label={`${item.count} dreams`}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <LinearProgress
                          variant="determinate"
                          value={item.similarity}
                          sx={{
                            mt: 1,
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: '#e0e0e0',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getSimilarityColor(item.similarity)
                            }
                          }}
                        />
                      }
                    />
                  </ListItem>
                ))}
              </List>
              
              {/* Pagination */}
              {similarTitles.length > itemsPerPage && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={getTotalPages()}
                    page={currentPage}
                    onChange={(e, page) => setCurrentPage(page)}
                    color="primary"
                    size="large"
                    showFirstButton
                    showLastButton
                  />
                </Box>
              )}

              {selectedForMerge.length > 0 && (
                <Box sx={{ mt: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Selected for merge:
                  </Typography>
                  <Typography variant="body2">
                    Total dreams to merge: {selectedForMerge.reduce((sum, t) => sum + t.count, 0)}
                  </Typography>
                  <Typography variant="body2">
                    After merge: {selectedTitle.count + selectedForMerge.reduce((sum, t) => sum + t.count, 0)} dreams
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        )}

        {/* Status Messages */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}

        {success && (
          <Grid item xs={12}>
            <Alert severity="success" onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default SimilaritySearch;