import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
} from '@mui/material';
import {
  Speed,
  Assessment,
  Warning,
  CheckCircle,
  BugReport,
  Code,
  Timeline,
} from '@mui/icons-material';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { getSeverityColor, getCategoryIcon } from '../../utils/formatters';

const ReportSummary = ({ summary, metrics }) => {
  if (!summary) {
    return (
      <Alert severity="warning">
        <Typography>No summary data available</Typography>
      </Alert>
    );
  }

  const qualityScoreColor = (score) => {
    if (score >= 80) return '#4caf50'; // green
    if (score >= 60) return '#ff9800'; // orange  
    return '#f44336'; // red
  };

  const getScoreGrade = (score) => {
    if (score >= 90) return 'A+';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C';
    if (score >= 50) return 'D';
    return 'F';
  };

  // Prepare chart data - moved outside conditional logic
  const severityData = React.useMemo(() => {
    if (!summary.issue_summary) return [];
    
    return summary.issue_summary.map(item => ({
      name: item.severity.charAt(0).toUpperCase() + item.severity.slice(1),
      value: item.count,
      color: getSeverityColor(item.severity)
    }));
  }, [summary.issue_summary]);

  const categoryData = React.useMemo(() => {
    if (!summary.issue_summary) return [];
    
    const categoryMap = {};
    summary.issue_summary.forEach(item => {
      if (!categoryMap[item.category]) {
        categoryMap[item.category] = 0;
      }
      categoryMap[item.category] += item.count;
    });
    
    return Object.entries(categoryMap).map(([category, count]) => ({
      category: category.replace('_', ' '),
      count,
      icon: getCategoryIcon(category)
    }));
  }, [summary.issue_summary]);

  // Quality scores data for chart
  const qualityData = summary.quality_score ? [
    { name: 'Overall', score: summary.quality_score.overall_score },
    { name: 'Security', score: summary.quality_score.security_score },
    { name: 'Performance', score: summary.quality_score.performance_score },
    { name: 'Maintainability', score: summary.quality_score.maintainability_score },
    { name: 'Test Coverage', score: summary.quality_score.test_coverage_score },
  ] : [];

  return (
    <Box>
      {/* Overall Quality Score */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ textAlign: 'center', py: 3 }}>
            <CardContent>
              <Typography variant="h3" gutterBottom>
                <Assessment sx={{ fontSize: 48, mr: 2, verticalAlign: 'middle' }} />
                Overall Quality Score
              </Typography>
              <Typography 
                variant="h1" 
                sx={{ 
                  color: qualityScoreColor(summary.quality_score?.overall_score || 0),
                  fontSize: '4rem',
                  fontWeight: 'bold'
                }}
              >
                {Math.round(summary.quality_score?.overall_score || 0)}
              </Typography>
              <Typography variant="h4" color="text.secondary">
                Grade: {getScoreGrade(summary.quality_score?.overall_score || 0)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={summary.quality_score?.overall_score || 0}
                sx={{ 
                  mt: 2, 
                  height: 10, 
                  borderRadius: 5,
                  bgcolor: 'grey.300',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: qualityScoreColor(summary.quality_score?.overall_score || 0),
                    borderRadius: 5,
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quality Breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={qualityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value) => [`${Math.round(value)}%`, 'Score']}
                  />
                  <Bar 
                    dataKey="score" 
                    fill="#3f51b5"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center' }}>
            <CardContent>
              <BugReport sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
              <Typography variant="h4" color="error.main">
                {summary.total_issues}
              </Typography>
              <Typography color="text.secondary">
                Total Issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center' }}>
            <CardContent>
              <Warning sx={{ fontSize: 40, color: 'error.dark', mb: 1 }} />
              <Typography variant="h4" color="error.dark">
                {summary.critical_issues}
              </Typography>
              <Typography color="text.secondary">
                Critical Issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center' }}>
            <CardContent>
              <Speed sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" color="warning.main">
                {summary.high_priority_issues}
              </Typography>
              <Typography color="text.secondary">
                High Priority
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center' }}>
            <CardContent>
              <Code sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" color="info.main">
                {metrics?.total_files || 0}
              </Typography>
              <Typography color="text.secondary">
                Files Analyzed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Issues by Severity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Issues by Severity
              </Typography>
              {severityData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={severityData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({name, value, percent}) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                      labelLine={false}
                    >
                      {severityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box textAlign="center" py={4}>
                  <CheckCircle sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
                  <Typography variant="h6" color="success.main">
                    No Issues Found!
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Issues by Category */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Issues by Category
              </Typography>
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categoryData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis 
                      type="category" 
                      dataKey="category" 
                      tick={{ fontSize: 12 }}
                      width={100}
                    />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3f51b5" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography variant="body1" color="text.secondary">
                    No category data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Information */}
      <Grid container spacing={3}>
        {/* Top Issues */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
                Top Critical Issues
              </Typography>
              
              {summary.top_issues && summary.top_issues.length > 0 ? (
                <List dense>
                  {summary.top_issues.slice(0, 5).map((issue, index) => (
                    <React.Fragment key={issue.id}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemIcon>
                          <Chip
                            label={index + 1}
                            size="small"
                            sx={{ 
                              backgroundColor: getSeverityColor(issue.severity),
                              color: 'white',
                              fontWeight: 'bold'
                            }}
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <span>{getCategoryIcon(issue.category)}</span>
                              <Typography variant="subtitle2" noWrap>
                                {issue.title}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary" noWrap>
                                {issue.file_path}
                                {issue.line_number && ` (line ${issue.line_number})`}
                              </Typography>
                              <Box display="flex" gap={0.5} mt={0.5}>
                                <Chip 
                                  label={issue.severity} 
                                  size="small" 
                                  sx={{ 
                                    backgroundColor: getSeverityColor(issue.severity),
                                    color: 'white'
                                  }}
                                />
                                <Chip 
                                  label={issue.category.replace('_', ' ')} 
                                  size="small" 
                                  variant="outlined" 
                                />
                                <Chip 
                                  label={`Impact: ${issue.impact_score?.toFixed(1)}`} 
                                  size="small" 
                                  variant="outlined"
                                  color="warning"
                                />
                              </Box>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < summary.top_issues.slice(0, 5).length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box textAlign="center" py={2}>
                  <CheckCircle sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="body1" color="success.main">
                    No critical issues found!
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <CheckCircle sx={{ mr: 1, verticalAlign: 'middle', color: 'success.main' }} />
                Recommendations
              </Typography>
              
              {summary.recommendations && summary.recommendations.length > 0 ? (
                <List dense>
                  {summary.recommendations.map((recommendation, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Chip
                          label={index + 1}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Typography variant="body2">
                            {recommendation}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Great job! Your code quality is excellent with no specific recommendations needed.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Repository Information */}
      {metrics && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Repository Statistics
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" color="primary.main">
                        {metrics.total_files?.toLocaleString() || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Files
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" color="info.main">
                        {metrics.total_lines?.toLocaleString() || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Lines of Code
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" color="warning.main">
                        {metrics.complexity_average?.toFixed(2) || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Complexity
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" color="success.main">
                        {metrics.maintainability_average?.toFixed(1) || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Maintainability
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                {/* Technical Debt */}
                {metrics.technical_debt_hours && (
                  <Box mt={3} textAlign="center">
                    <Typography variant="h6" gutterBottom>
                      Technical Debt Estimate
                    </Typography>
                    <Typography variant="h4" color="error.main">
                      {Math.round(metrics.technical_debt_hours)} hours
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Estimated time to resolve all issues
                    </Typography>
                  </Box>
                )}
                
                {/* Languages Distribution */}
                {metrics.languages && Object.keys(metrics.languages).length > 0 && (
                  <Box mt={3}>
                    <Typography variant="subtitle1" gutterBottom>
                      Languages Distribution
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {Object.entries(metrics.languages)
                        .sort(([,a], [,b]) => b - a)
                        .map(([lang, count]) => (
                          <Chip
                            key={lang}
                            label={`${lang}: ${count} files`}
                            variant="outlined"
                            size="small"
                            color="primary"
                          />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default ReportSummary;