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
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterAlt as FilterIcon,
  GetApp as ExportIcon,
  Visibility as ViewIcon,
  Category as CategoryIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import api from '../utils/api';

const AGE_GROUPS = {
  'Under 13': { min: 0, max: 12 },
  '13-18': { min: 13, max: 18 },
  '19-30': { min: 19, max: 30 },
  '31-45': { min: 31, max: 45 },
  '46-60': { min: 46, max: 60 },
  '60+': { min: 60, max: 100 },
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'];

const CategoryDetailsModal = ({ open, onClose, categoryData, viewType }) => {
  const [categoryDreams, setCategoryDreams] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && categoryData) {
      fetchCategoryDreams();
    }
  }, [open, categoryData]);

  const fetchCategoryDreams = async () => {
    if (!categoryData) return;
    
    setLoading(true);
    try {
      const response = await api.get('/category-dreams', {
        params: { 
          category: categoryData.category,
          type: viewType || 'categories'
        }
      });
      setCategoryDreams(response.data.dreams || []);
    } catch (error) {
      console.error('Failed to fetch category dreams:', error);
      setCategoryDreams([]);
    } finally {
      setLoading(false);
    }
  };

  if (!categoryData) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <CategoryIcon color="primary" />
          <Typography variant="h6">
            Category: {categoryData.category}
          </Typography>
          <Chip 
            label={`${categoryData.count} dreams`} 
            color="primary" 
            size="small" 
          />
        </Box>
      </DialogTitle>
      <DialogContent>
        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Dreams in this category:
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Normalized Title</TableCell>
                    <TableCell align="right">Count</TableCell>
                    <TableCell>Age Range</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {categoryDreams.slice(0, 20).map((dream, index) => (
                    <TableRow key={index}>
                      <TableCell>{dream.normalized_title}</TableCell>
                      <TableCell align="right">{dream.count}</TableCell>
                      <TableCell>
                        {dream.min_age && dream.max_age 
                          ? `${dream.min_age}-${dream.max_age}` 
                          : 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {categoryDreams.length > 20 && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                Showing first 20 of {categoryDreams.length} dreams
              </Typography>
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const CategoriesAnalysis = () => {
  const [categories, setCategories] = useState([]);
  const [filteredCategories, setFilteredCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [minCount, setMinCount] = useState(1);
  const [maxCount, setMaxCount] = useState(10000);
  const [minAge, setMinAge] = useState(13);
  const [maxAge, setMaxAge] = useState(60);
  const [appliedMinAge, setAppliedMinAge] = useState(13);
  const [appliedMaxAge, setAppliedMaxAge] = useState(60);
  const [sortBy, setSortBy] = useState('count');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewType, setViewType] = useState('categories'); // 'categories' or 'subcategories'
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  // Modal
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Fetch categories data
  const fetchCategories = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = viewType === 'categories' ? '/categories-analysis' : '/subcategories-analysis';
      const response = await api.get(endpoint, {
        params: {
          min_age: appliedMinAge,
          max_age: appliedMaxAge
        }
      });
      const data = response.data.categories || [];
      setCategories(data);
      setFilteredCategories(data);
      
      // Update max count slider
      if (data.length > 0) {
        const maxCategoryCount = Math.max(...data.map(cat => cat.count));
        setMaxCount(Math.min(maxCategoryCount, 10000));
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      setError('Failed to load categories data');
      setCategories([]);
      setFilteredCategories([]);
    } finally {
      setLoading(false);
    }
  }, [appliedMinAge, appliedMaxAge, viewType]);

  // Apply filters
  useEffect(() => {
    let filtered = categories.filter(category => {
      const matchesSearch = category.category.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCount = category.count >= minCount && category.count <= maxCount;
      return matchesSearch && matchesCount;
    });

    // Sort
    filtered.sort((a, b) => {
      let aVal, bVal;
      switch (sortBy) {
        case 'count':
          aVal = a.count;
          bVal = b.count;
          break;
        case 'category':
          aVal = a.category.toLowerCase();
          bVal = b.category.toLowerCase();
          break;
        case 'avg_age':
          aVal = a.avg_age || 0;
          bVal = b.avg_age || 0;
          break;
        default:
          aVal = a.count;
          bVal = b.count;
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    setFilteredCategories(filtered);
    setPage(0); // Reset to first page when filters change
  }, [categories, searchTerm, minCount, maxCount, sortBy, sortOrder]);

  // Load data on mount and when view type changes
  useEffect(() => {
    fetchCategories();
  }, [viewType, fetchCategories]);

  // Handle apply filters
  const handleApplyFilters = () => {
    setAppliedMinAge(minAge);
    setAppliedMaxAge(maxAge);
    fetchCategories();
  };

  // Handle category details
  const handleViewCategory = (category) => {
    setSelectedCategory(category);
    setModalOpen(true);
  };

  // Export data
  const handleExport = () => {
    const csvContent = [
      'Category,Count,Avg Age,Top Age Group,Gender Distribution',
      ...filteredCategories.map(cat => 
        `"${cat.category}",${cat.count},${cat.avg_age || 'N/A'},"${cat.top_age_group || 'N/A'}","${cat.gender_dist || 'N/A'}"`
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `categories_analysis_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  // Prepare chart data
  const topCategoriesData = filteredCategories.slice(0, 10).map(cat => ({
    category: cat.category.length > 20 ? cat.category.substring(0, 20) + '...' : cat.category,
    count: cat.count
  }));

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <div>
                <Typography variant="h4" gutterBottom>
                  <CategoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  {viewType === 'categories' ? 'Categories' : 'Subcategories'} Analysis
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                  Analyze dream {viewType}, distributions, and patterns
                </Typography>
              </div>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <ToggleButtonGroup
                  value={viewType}
                  exclusive
                  onChange={(e, newViewType) => newViewType && setViewType(newViewType)}
                  size="small"
                >
                  <ToggleButton value="categories">
                    Categories
                  </ToggleButton>
                  <ToggleButton value="subcategories">
                    Subcategories
                  </ToggleButton>
                </ToggleButtonGroup>
                
                <Button
                  variant="outlined"
                  startIcon={<ExportIcon />}
                  onClick={handleExport}
                  disabled={filteredCategories.length === 0}
                >
                  Export CSV
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Stats Overview */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {categories.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total {viewType === 'categories' ? 'Categories' : 'Subcategories'}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="secondary">
                    {categories.reduce((sum, cat) => sum + cat.count, 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Dreams
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {categories.length > 0 ? Math.round(categories.reduce((sum, cat) => sum + cat.count, 0) / categories.length) : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Dreams/{viewType === 'categories' ? 'Category' : 'Subcategory'}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {filteredCategories.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Filtered Results
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Chart */}
        {topCategoriesData.length > 0 && (
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Top {viewType === 'categories' ? 'Categories' : 'Subcategories'} by Dream Count
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={topCategoriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="category" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Filters */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Filters
            </Typography>
            
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label={`Search ${viewType}`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Sort by</InputLabel>
                  <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                    <MenuItem value="count">Dream Count</MenuItem>
                    <MenuItem value="category">{viewType === 'categories' ? 'Category' : 'Subcategory'} Name</MenuItem>
                    <MenuItem value="avg_age">Average Age</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Order</InputLabel>
                  <Select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                    <MenuItem value="desc">Descending</MenuItem>
                    <MenuItem value="asc">Ascending</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Typography gutterBottom>
                  Dream Count Range: {minCount} - {maxCount}
                </Typography>
                <Slider
                  value={[minCount, maxCount]}
                  onChange={(e, newValue) => {
                    setMinCount(newValue[0]);
                    setMaxCount(newValue[1]);
                  }}
                  valueLabelDisplay="auto"
                  min={1}
                  max={10000}
                />
              </Grid>
              
              <Grid item xs={12} md={5}>
                <Typography gutterBottom>
                  Age Range: {minAge} - {maxAge} years
                  {(minAge !== appliedMinAge || maxAge !== appliedMaxAge) && 
                    <Chip label="Not applied" size="small" color="warning" sx={{ ml: 1 }} />
                  }
                </Typography>
                <Slider
                  value={[minAge, maxAge]}
                  onChange={(e, newValue) => {
                    setMinAge(newValue[0]);
                    setMaxAge(newValue[1]);
                  }}
                  valueLabelDisplay="auto"
                  min={3}
                  max={125}
                  marks={[
                    { value: 3, label: '3' },
                    { value: 13, label: '13' },
                    { value: 18, label: '18' },
                    { value: 30, label: '30' },
                    { value: 45, label: '45' },
                    { value: 60, label: '60' },
                    { value: 125, label: '125' }
                  ]}
                />
              </Grid>
              
              <Grid item xs={12} md={1}>
                <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleApplyFilters}
                    startIcon={<RefreshIcon />}
                    disabled={loading || (minAge === appliedMinAge && maxAge === appliedMaxAge)}
                    fullWidth
                  >
                    Apply
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Categories Table */}
        <Grid item xs={12}>
          <Paper elevation={3}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>{viewType === 'categories' ? 'Category' : 'Subcategory'}</TableCell>
                    <TableCell align="right">Dream Count</TableCell>
                    <TableCell align="right">Avg Age</TableCell>
                    <TableCell>Top Age Group</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredCategories
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((category, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {category.category}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip 
                            label={category.count} 
                            color="primary" 
                            size="small" 
                          />
                        </TableCell>
                        <TableCell align="right">
                          {category.avg_age ? category.avg_age.toFixed(1) : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {category.top_age_group || 'N/A'}
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            size="small"
                            startIcon={<ViewIcon />}
                            onClick={() => handleViewCategory(category)}
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <TablePagination
              rowsPerPageOptions={[10, 25, 50, 100]}
              component="div"
              count={filteredCategories.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Category Details Modal */}
      <CategoryDetailsModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        categoryData={selectedCategory}
        viewType={viewType}
      />
    </Box>
  );
};

export default CategoriesAnalysis;