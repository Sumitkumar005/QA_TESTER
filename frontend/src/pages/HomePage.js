// frontend/src/pages/HomePage.js
import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
} from '@mui/material';
import { Link } from 'react-router-dom';
import {
  Security,
  Speed,
  BugReport,
  Assessment,
  QuestionAnswer,
  GitHub,
} from '@mui/icons-material';

const features = [
  {
    icon: <Security color="primary" />,
    title: 'Security Analysis',
    description: 'Detect security vulnerabilities and potential exploits in your codebase.',
  },
  {
    icon: <Speed color="primary" />,
    title: 'Performance Optimization',
    description: 'Identify performance bottlenecks and optimization opportunities.',
  },
  {
    icon: <BugReport color="primary" />,
    title: 'Code Quality Issues',
    description: 'Find code quality problems, complexity issues, and maintainability concerns.',
  },
  {
    icon: <Assessment color="primary" />,
    title: 'Detailed Reports',
    description: 'Get comprehensive reports with actionable recommendations.',
  },
  {
    icon: <QuestionAnswer color="primary" />,
    title: 'Interactive Q&A',
    description: 'Ask questions about your codebase and get intelligent answers.',
  },
  {
    icon: <GitHub color="primary" />,
    title: 'GitHub Integration',
    description: 'Analyze repositories directly from GitHub URLs.',
  },
];

const supportedLanguages = [
  'Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust',
  'C++', 'C', 'C#', 'Ruby', 'PHP', 'Kotlin'
];

const HomePage = () => {
  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box textAlign="center" py={8}>
        <Typography variant="h2" component="h1" gutterBottom>
          AI-Powered Code Quality Intelligence
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Analyze your codebase, identify quality issues, and get actionable insights
          powered by advanced AI and AST parsing.
        </Typography>
        <Box mt={4}>
          <Button
            variant="contained"
            size="large"
            component={Link}
            to="/analyze"
            sx={{ mr: 2 }}
          >
            Start Analysis
          </Button>
          <Button
            variant="outlined"
            size="large"
            component={Link}
            to="/qa"
          >
            Ask Questions
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box py={6}>
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
          Features
        </Typography>
        <Grid container spacing={4} mt={2}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    {feature.icon}
                    <Typography variant="h6" component="h3" ml={1}>
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Supported Languages */}
      <Box py={6}>
        <Typography variant="h4" component="h2" textAlign="center" gutterBottom>
          Supported Languages
        </Typography>
        <Box display="flex" flexWrap="wrap" justifyContent="center" gap={1} mt={3}>
          {supportedLanguages.map((language) => (
            <Chip key={language} label={language} variant="outlined" />
          ))}
        </Box>
      </Box>

      {/* Getting Started */}
      <Box py={6}>
        <Typography variant="h4" component="h2" textAlign="center" gutterBottom>
          Getting Started
        </Typography>
        <Grid container spacing={4} mt={2}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  1. Upload or Connect
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Upload your code files or connect a GitHub repository.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  2. Run Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Our AI analyzes your code for quality, security, and performance issues.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  3. Get Insights
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Review detailed reports and ask questions about your codebase.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage;