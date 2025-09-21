import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  TextField,
  MenuItem,
  Grid,
  Pagination,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore,
  Security,
  Speed,
  BugReport,
  Build,
  Assessment,
  Description,
  Warning,
} from '@mui/icons-material';
import { getSeverityColor } from '../../utils/formatters';

const IssuesList = ({ issues = [] }) => {
  const [filter, setFilter] = useState({
    severity: 'all',
    category: 'all',
    search: '',
  });
  const [page, setPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Filter and search issues
  const filteredIssues = useMemo(() => {
    return issues.filter(issue => {
      const matchesSeverity = filter.severity === 'all' || issue.severity === filter.severity;
      const matchesCategory = filter.category === 'all' || issue.category === filter.category;
      const matchesSearch = filter.search === '' || 
        issue.title.toLowerCase().includes(filter.search.toLowerCase()) ||
        issue.description.toLowerCase().includes(filter.search.toLowerCase()) ||
        issue.file_path.toLowerCase().includes(filter.search.toLowerCase());
      
      return matchesSeverity && matchesCategory && matchesSearch;
    });
  }, [issues, filter]);

  // Paginated issues
  const paginatedIssues = useMemo(() => {
    const startIndex = (page - 1) * itemsPerPage;
    return filteredIssues.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredIssues, page, itemsPerPage]);

  const totalPages = Math.ceil(filteredIssues.length / itemsPerPage);

  const getCategoryColor = (category) => {
    const colors = {
      security: 'error',
      performance: 'warning',
      code_quality: 'info',
      maintainability: 'primary',
      testing: 'secondary',
      documentation: 'default',
    };
    return colors[category] || 'default';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      security: <Security />,
      performance: <Speed />,
      code_quality: <BugReport />,
      maintainability: <Build />,
      testing: <Assessment />,
      documentation: <Description />,
    };
    return icons[category] || <Warning />;
  };

  if (!issues || issues.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No issues found!
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Your code quality is excellent. Keep up the good work!
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Issues Found ({issues.length})
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search issues"
                value={filter.search}
                onChange={(e) => setFilter({ ...filter, search: e.target.value })}
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                label="Filter by Severity"
                value={filter.severity}
                onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                size="small"
              >
                <MenuItem value="all">All Severities</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="info">Info</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                label="Filter by Category"
                value={filter.category}
                onChange={(e) => setFilter({ ...filter, category: e.target.value })}
                size="small"
              >
                <MenuItem value="all">All Categories</MenuItem>
                <MenuItem value="security">Security</MenuItem>
                <MenuItem value="performance">Performance</MenuItem>
                <MenuItem value="code_quality">Code Quality</MenuItem>
                <MenuItem value="maintainability">Maintainability</MenuItem>
                <MenuItem value="testing">Testing</MenuItem>
                <MenuItem value="documentation">Documentation</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Issues List */}
      {paginatedIssues.map((issue, index) => (
        <Accordion key={issue.id} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" alignItems="center" width="100%" mr={2}>
              <Box display="flex" alignItems="center" flex={1}>
                {getCategoryIcon(issue.category)}
                <Box ml={2} flex={1}>
                  <Typography variant="subtitle1" component="div">
                    {issue.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {issue.file_path} {issue.line_number && `(line ${issue.line_number})`}
                  </Typography>
                </Box>
              </Box>
              <Box display="flex" gap={1}>
                <Chip
                  label={issue.severity}
                  size="small"
                  sx={{
                    backgroundColor: getSeverityColor(issue.severity),
                    color: 'white',
                  }}
                />
                <Chip
                  label={issue.category}
                  size="small"
                  color={getCategoryColor(issue.category)}
                  variant="outlined"
                />
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="body1" paragraph>
                <strong>Description:</strong> {issue.description}
              </Typography>
              
              <Typography variant="body1" paragraph>
                <strong>Suggestion:</strong> {issue.suggestion}
              </Typography>

              {issue.code_snippet && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Code:
                  </Typography>
                  <Box
                    component="pre"
                    sx={{
                      backgroundColor: '#2d2d2d',
                      color: '#fff',
                      p: 2,
                      borderRadius: 1,
                      overflow: 'auto',
                      fontSize: '0.875rem',
                      fontFamily: 'monospace',
                    }}
                  >
                    {issue.code_snippet}
                  </Box>
                </Box>
              )}

              <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                <Box display="flex" gap={1}>
                  <Chip label={`Impact: ${issue.impact_score?.toFixed(1) || 'N/A'}`} size="small" />
                  <Chip label={`Confidence: ${((issue.confidence || 0) * 100).toFixed(0)}%`} size="small" />
                </Box>
                {issue.tags && issue.tags.length > 0 && (
                  <Box display="flex" gap={0.5}>
                    {issue.tags.slice(0, 3).map(tag => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                )}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(e, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}

      {filteredIssues.length === 0 && issues.length > 0 && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="text.secondary">
            No issues match your filters
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search criteria
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default IssuesList;