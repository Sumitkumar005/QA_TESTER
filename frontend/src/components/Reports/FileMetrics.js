import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  MenuItem,
  TablePagination,
  LinearProgress,
  Alert,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const FileMetrics = ({ fileMetrics = [], metrics = null }) => {
  const [filter, setFilter] = useState({
    language: 'all',
    search: '',
    sortBy: 'complexity',
    sortOrder: 'desc',
  });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Filter and sort file metrics
  const filteredMetrics = useMemo(() => {
    if (!Array.isArray(fileMetrics)) {
      return [];
    }

    let filtered = fileMetrics.filter(file => {
      const matchesLanguage = filter.language === 'all' || file.language === filter.language;
      const matchesSearch = filter.search === '' ||
        file.file_path?.toLowerCase().includes(filter.search.toLowerCase());

      return matchesLanguage && matchesSearch;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue, bValue;

      switch (filter.sortBy) {
        case 'complexity':
          aValue = a.complexity || 0;
          bValue = b.complexity || 0;
          break;
        case 'maintainability':
          aValue = a.maintainability_index || 0;
          bValue = b.maintainability_index || 0;
          break;
        case 'lines':
          aValue = a.lines_of_code || 0;
          bValue = b.lines_of_code || 0;
          break;
        case 'issues':
          aValue = a.issues_count || 0;
          bValue = b.issues_count || 0;
          break;
        default:
          aValue = a.file_path || '';
          bValue = b.file_path || '';
      }

      if (filter.sortOrder === 'desc') {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      } else {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [fileMetrics, filter]);

  // Paginated metrics
  const paginatedMetrics = useMemo(() => {
    return filteredMetrics.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [filteredMetrics, page, rowsPerPage]);

  // Chart data for top complex files
  const chartData = useMemo(() => {
    return filteredMetrics
      .slice(0, 10)
      .map(file => ({
        name: file.file_path?.split('/').pop() || 'Unknown',
        complexity: file.complexity || 0,
        maintainability: file.maintainability_index || 0,
        issues: file.issues_count || 0,
      }));
  }, [filteredMetrics]);

  const getComplexityColor = (complexity) => {
    if (complexity <= 5) return 'success';
    if (complexity <= 10) return 'warning';
    return 'error';
  };

  const getMaintainabilityColor = (index) => {
    if (index >= 80) return 'success';
    if (index >= 60) return 'warning';
    return 'error';
  };

  const getLanguageColor = (language) => {
    const colors = {
      python: '#3776ab',
      javascript: '#f7df1e',
      typescript: '#3178c6',
      java: '#007396',
      go: '#00add8',
      rust: '#000000',
      cpp: '#00599c',
      csharp: '#239120',
      ruby: '#cc342d',
      php: '#777bb4',
    };
    return colors[language?.toLowerCase()] || '#666666';
  };

  const uniqueLanguages = useMemo(() => {
    if (!Array.isArray(fileMetrics)) return [];
    return [...new Set(fileMetrics.map(f => f.language).filter(Boolean))];
  }, [fileMetrics]);

  if (!fileMetrics || fileMetrics.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Alert severity="info">
          <Typography variant="h6" color="text.secondary">
            No file metrics available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            File-level metrics will appear here once analysis is complete.
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        File Metrics ({fileMetrics.length} files)
      </Typography>

      {/* Summary Cards */}
      {metrics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {metrics.total_files || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Files
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {metrics.total_lines?.toLocaleString() || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Lines
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {metrics.complexity_average?.toFixed(2) || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Complexity
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {metrics.maintainability_average?.toFixed(2) || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Maintainability
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Chart */}
      {chartData.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Complex Files
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  interval={0}
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="complexity" fill="#ff9800" name="Complexity" />
                <Bar dataKey="issues" fill="#f44336" name="Issues" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search files"
                value={filter.search}
                onChange={(e) => setFilter({ ...filter, search: e.target.value })}
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                select
                fullWidth
                label="Filter by Language"
                value={filter.language}
                onChange={(e) => setFilter({ ...filter, language: e.target.value })}
                size="small"
              >
                <MenuItem value="all">All Languages</MenuItem>
                {uniqueLanguages.map(lang => (
                  <MenuItem key={lang} value={lang}>{lang}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                select
                fullWidth
                label="Sort by"
                value={filter.sortBy}
                onChange={(e) => setFilter({ ...filter, sortBy: e.target.value })}
                size="small"
              >
                <MenuItem value="complexity">Complexity</MenuItem>
                <MenuItem value="maintainability">Maintainability</MenuItem>
                <MenuItem value="lines">Lines of Code</MenuItem>
                <MenuItem value="issues">Issues Count</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                select
                fullWidth
                label="Order"
                value={filter.sortOrder}
                onChange={(e) => setFilter({ ...filter, sortOrder: e.target.value })}
                size="small"
              >
                <MenuItem value="desc">Descending</MenuItem>
                <MenuItem value="asc">Ascending</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* File Metrics Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>File</TableCell>
                <TableCell>Language</TableCell>
                <TableCell align="right">Lines</TableCell>
                <TableCell align="right">Complexity</TableCell>
                <TableCell align="right">Maintainability</TableCell>
                <TableCell align="right">Issues</TableCell>
                <TableCell>Health</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedMetrics.map((file, index) => (
                <TableRow key={`${file.file_path}-${index}`} hover>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {file.file_path || 'Unknown'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={file.language || 'Unknown'}
                      size="small"
                      sx={{
                        backgroundColor: getLanguageColor(file.language),
                        color: file.language?.toLowerCase() === 'javascript' ? 'black' : 'white',
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    {(file.lines_of_code || 0).toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={(file.complexity || 0).toFixed(1)}
                      color={getComplexityColor(file.complexity || 0)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={(file.maintainability_index || 0).toFixed(1)}
                      color={getMaintainabilityColor(file.maintainability_index || 0)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={file.issues_count || 0}
                      color={(file.issues_count || 0) > 5 ? 'error' : (file.issues_count || 0) > 2 ? 'warning' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(((file.maintainability_index || 0) / 100) * 100, 100)}
                      sx={{ 
                        width: 60,
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getMaintainabilityColor(file.maintainability_index || 0) === 'success' ? '#4caf50' : 
                                          getMaintainabilityColor(file.maintainability_index || 0) === 'warning' ? '#ff9800' : '#f44336'
                        }
                      }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={filteredMetrics.length}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>
    </Box>
  );
};

export default FileMetrics;