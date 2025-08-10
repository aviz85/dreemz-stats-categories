import React, { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Typography,
  TextField,
  Box,
  Slider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Alert,
  CircularProgress,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterAlt as FilterIcon,
  GetApp as ExportIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { dashboardApi } from '../utils/api';

const AGE_GROUPS = {
  'Under 13': { min: 0, max: 12 },
  '13-18': { min: 13, max: 18 },
  '19-30': { min: 19, max: 30 },
  '31-45': { min: 31, max: 45 },
  '46-60': { min: 46, max: 60 },
  '60+': { min: 60, max: 100 },
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const DreamDetailsModal = ({ open, onClose, normalizedTitle }) => {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && normalizedTitle) {
      setLoading(true);
      dashboardApi.getDreamDetails(normalizedTitle)
        .then(response => {
          setDetails(response.data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to fetch dream details:', err);
          setLoading(false);
        });
    }
  }, [open, normalizedTitle]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Dream Analysis: "{normalizedTitle}"
      </DialogTitle>
      <DialogContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : details ? (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Age Group Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    dataKey="count"
                    data={details.age_distribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    label={({ age_group, count }) => `${age_group}: ${count}`}
                  >
                    {details.age_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Category Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={details.category_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" angle={-45} textAnchor="end" height={60} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Sample Original Dreams ({details.sample_dreams.length} shown)
              </Typography>
              <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                {details.sample_dreams.map((dream, index) => (
                  <Box key={dream.dream_id} sx={{ p: 2, borderBottom: '1px solid #f0f0f0' }}>
                    <Typography variant="body2" color="text.secondary">
                      #{dream.dream_id} ({dream.age_group}): {dream.original_title}
                    </Typography>
                    <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {dream.categories.map((cat, catIndex) => (
                        <Chip
                          key={catIndex}
                          label={`${cat.category} / ${cat.subcategory}`}
                          size="small"
                          color={catIndex === 0 ? 'primary' : catIndex === 1 ? 'secondary' : 'success'}
                          variant={catIndex === 0 ? 'filled' : 'outlined'}
                        />
                      ))}
                    </Box>
                  </Box>
                ))}
              </Box>
            </Grid>
          </Grid>
        ) : (
          <Alert severity="error">Failed to load dream details</Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

const UniqueDreams = () => {
  const [dreams, setDreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalUnique, setTotalUnique] = useState(0);
  const [totalDreams, setTotalDreams] = useState(0);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [ageRange, setAgeRange] = useState([13, 60]);
  const [sortBy, setSortBy] = useState('count');
  const [sortOrder, setSortOrder] = useState('desc');

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);

  // Modal
  const [detailsModal, setDetailsModal] = useState({ open: false, title: null });

  const fetchDreams = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        search: searchTerm,
        age_from: ageRange[0],
        age_to: ageRange[1],
        limit: rowsPerPage,
        offset: page * rowsPerPage,
        sort: sortBy,
        order: sortOrder,
      };

      const response = await dashboardApi.getUniqueDreams(params);
      const data = response.data;

      setDreams(data.dreams || []);
      setTotalUnique(data.total_unique || 0);
      setTotalDreams(data.total_dreams || 0);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch unique dreams:', err);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, ageRange, sortBy, sortOrder, page, rowsPerPage]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchDreams();
    }, 300); // Debounce search

    return () => clearTimeout(timeoutId);
  }, [fetchDreams]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(0); // Reset to first page on search
  };

  const handleAgeRangeChange = (event, newValue) => {
    setAgeRange(newValue);
    setPage(0);
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSortChange = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder(field === 'count' ? 'desc' : 'asc');
    }
    setPage(0);
  };

  const exportToCsv = () => {
    const headers = ['Normalized Title', 'Count', 'Age Groups'];
    const csvContent = [
      headers.join(','),
      ...dreams.map(dream => [
        `"${dream.normalized_title}"`,
        dream.count,
        `"${(dream.age_groups || []).join(', ')}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `unique-dreams-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const openDetailsModal = (normalizedTitle) => {
    setDetailsModal({ open: true, title: normalizedTitle });
  };

  const closeDetailsModal = () => {
    setDetailsModal({ open: false, title: null });
  };

  return (
    <Box>
      {/* Header Stats */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom>
              Unique Normalized Dreams Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {totalUnique.toLocaleString()} unique normalized dreams from {totalDreams.toLocaleString()} total dreams
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
            <Button
              variant="outlined"
              startIcon={<ExportIcon />}
              onClick={exportToCsv}
              disabled={dreams.length === 0}
            >
              Export CSV
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search Dreams"
              variant="outlined"
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              placeholder="e.g., become doctor, buy house..."
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>
              Age Range: {ageRange[0]} - {ageRange[1]}+ years
            </Typography>
            <Slider
              value={ageRange}
              onChange={handleAgeRangeChange}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              marks={[
                { value: 13, label: '13' },
                { value: 18, label: '18' },
                { value: 30, label: '30' },
                { value: 45, label: '45' },
                { value: 60, label: '60+' },
              ]}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={`${sortBy}-${sortOrder}`}
                label="Sort By"
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  setSortBy(field);
                  setSortOrder(order);
                  setPage(0);
                }}
              >
                <MenuItem value="count-desc">Count (High to Low)</MenuItem>
                <MenuItem value="count-asc">Count (Low to High)</MenuItem>
                <MenuItem value="title-asc">Title (A to Z)</MenuItem>
                <MenuItem value="title-desc">Title (Z to A)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Results Table */}
      <Paper>
        {error ? (
          <Alert severity="error" sx={{ m: 2 }}>
            Error: {error}
            <Button onClick={fetchDreams} sx={{ ml: 2 }}>
              Retry
            </Button>
          </Alert>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell 
                      sx={{ cursor: 'pointer' }} 
                      onClick={() => handleSortChange('title')}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        Normalized Dream
                        {sortBy === 'title' && (
                          <Typography variant="caption" sx={{ ml: 1 }}>
                            {sortOrder === 'asc' ? '↑' : '↓'}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell 
                      sx={{ cursor: 'pointer' }} 
                      onClick={() => handleSortChange('count')}
                      align="right"
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        Count
                        {sortBy === 'count' && (
                          <Typography variant="caption" sx={{ ml: 1 }}>
                            {sortOrder === 'asc' ? '↑' : '↓'}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>Age Groups</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={4} sx={{ textAlign: 'center', py: 4 }}>
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : dreams.length > 0 ? (
                    dreams.map((dream, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Typography variant="body1" fontWeight={500}>
                            {dream.normalized_title}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip 
                            label={dream.count.toLocaleString()} 
                            color="primary" 
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {(dream.age_groups || []).slice(0, 3).map((ageGroup, idx) => (
                              <Chip 
                                key={idx}
                                label={ageGroup} 
                                size="small" 
                                variant="outlined"
                              />
                            ))}
                            {(dream.age_groups || []).length > 3 && (
                              <Chip 
                                label={`+${(dream.age_groups || []).length - 3}`}
                                size="small" 
                                variant="outlined"
                                color="secondary"
                              />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            startIcon={<ViewIcon />}
                            onClick={() => openDetailsModal(dream.normalized_title)}
                          >
                            Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={4} sx={{ textAlign: 'center', py: 4 }}>
                        <Alert severity="info">
                          No unique dreams found. Try adjusting your search filters or start the V3 pipeline to normalize dreams.
                        </Alert>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {!loading && dreams.length > 0 && (
              <TablePagination
                rowsPerPageOptions={[25, 50, 100]}
                component="div"
                count={totalUnique}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handlePageChange}
                onRowsPerPageChange={handleRowsPerPageChange}
              />
            )}
          </>
        )}
      </Paper>

      {/* Details Modal */}
      <DreamDetailsModal
        open={detailsModal.open}
        onClose={closeDetailsModal}
        normalizedTitle={detailsModal.title}
      />
    </Box>
  );
};

export default UniqueDreams;