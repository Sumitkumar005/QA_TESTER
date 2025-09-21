import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  Warning,
  Error,
  Info,
  Assessment,
  QuestionAnswer,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const AnalysisResults = ({ results }) => {
  const navigate = useNavigate();

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#d32f2f',
      high: '#f57c00',
      medium: '#fbc02d',
      low: '#388e3c',
      info: '#1976d2'
    };
    return colors[severity] || '#9e9e9e';
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <Error sx={{ color: getSeverityColor(severity) }} />;
      case 'high':
        return <Warning sx={{ color: getSeverityColor(severity) }} />;
      case 'medium':
        return <Info sx={{ color: getSeverityColor(severity) }} />;
      default:
        return <CheckCircle sx={{ color: getSeverityColor(severity) }} />;
    }
  };

  // Prepare chart data - moved outside conditional logic
  const severityData = React.useMemo(() => {
    if (!results?.issues || results.issues.length === 0) {
      return [];
    }
    
    const counts = {};
    results.issues.forEach(issue => {
      counts[issue.severity] = (counts[issue.severity] || 0) + 1;
    });
    
    return Object.entries(counts).map(([severity, count]) => ({
      name: severity,
      value: count,
      color: getSeverityColor(severity)
    }));
  }, [results?.issues]);

  if (!results) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6" color="text.secondary">
          No results available
        </Typography>
      </Box>
    );
  }

  const handleViewReport = () => {
    navigate(`/report/${results.report_id}`);
  };

  const handleAskQuestions = () => {
    navigate(`/qa/${results.report_id}`);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analysis Complete!
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Issues
              </Typography>
              <Typography variant="h4" color="error">
                {results.issues?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Files Analyzed
              </Typography>
              <Typography variant="h4" color="primary">
                {results.file_metrics?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Lines of Code
              </Typography>
              <Typography variant="h4" color="info.main">
                {results.metrics?.total_lines?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Quality Score
              </Typography>
              <Typography variant="h4" color="success.main">
                {results.quality_score ? Math.round(results.quality_score) : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Issues Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Issues by Severity
              </Typography>
              
              {results.issues && results.issues.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={severityData}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({name, value}) => `${name}: ${value}`}
                      >
                        {severityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  
                  <Box mt={2}>
                    {['critical', 'high', 'medium', 'low', 'info'].map(severity => {
                      const count = results.issues.filter(issue => issue.severity === severity).length;
                      if (count === 0) return null;
                      
                      return (
                        <Box key={severity} display="flex" alignItems="center" mb={1}>
                          {getSeverityIcon(severity)}
                          <Typography variant="body2" sx={{ ml: 1, flex: 1 }}>
                            {severity.charAt(0).toUpperCase() + severity.slice(1)}
                          </Typography>
                          <Chip label={count} size="small" />
                        </Box>
                      );
                    })}
                  </Box>
                </>
              ) : (
                <Alert severity="success" sx={{ mt: 2 }}>
                  <Typography variant="body1">
                    Excellent! No issues found in your codebase.
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top Issues */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Issues
              </Typography>
              
              {results.issues && results.issues.length > 0 ? (
                <Box>
                  {results.issues.slice(0, 5).map((issue, index) => (
                    <Box key={issue.id} mb={2} p={2} sx={{ 
                      border: 1, 
                      borderColor: 'divider',
                      borderRadius: 1,
                      borderLeft: 4,
                      borderLeftColor: getSeverityColor(issue.severity)
                    }}>
                      <Box display="flex" alignItems="center" mb={1}>
                        {getSeverityIcon(issue.severity)}
                        <Typography variant="subtitle2" sx={{ ml: 1, flex: 1 }}>
                          {issue.title}
                        </Typography>
                        <Chip 
                          label={issue.severity} 
                          size="small" 
                          sx={{ 
                            backgroundColor: getSeverityColor(issue.severity),
                            color: 'white'
                          }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {issue.file_path} 
                        {issue.line_number && ` (line ${issue.line_number})`}
                      </Typography>
                    </Box>
                  ))}
                  
                  {results.issues.length > 5 && (
                    <Typography variant="body2" color="text.secondary" textAlign="center">
                      And {results.issues.length - 5} more issues...
                    </Typography>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No issues to display
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Languages */}
        {results.metrics?.languages && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Languages Analyzed
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {Object.entries(results.metrics.languages).map(([lang, count]) => (
                    <Chip
                      key={lang}
                      label={`${lang} (${count} files)`}
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                What's Next?
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Assessment />}
                    onClick={handleViewReport}
                    size="large"
                  >
                    View Detailed Report
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<QuestionAnswer />}
                    onClick={handleAskQuestions}
                    size="large"
                  >
                    Ask Questions
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => window.location.reload()}
                    size="large"
                  >
                    Analyze Another Project
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalysisResults;