import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Button,
  Breadcrumbs,
} from '@mui/material';
import { QuestionAnswer, GetApp, Share } from '@mui/icons-material';
import { reportsService } from '../services/api';
import { toast } from 'react-toastify';

import ReportSummary from '../components/Reports/ReportSummary';
import IssuesList from '../components/Reports/IssuesList';
import FileMetrics from '../components/Reports/FileMetrics';
// import QualityTrends from '../components/Reports/QualityTrends';

const ReportPage = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        const reportData = await reportsService.getReport(reportId, true);
        setReport(reportData);
      } catch (err) {
        setError(err.message);
        toast.error(`Failed to load report: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    if (reportId) {
      fetchReport();
    }
  }, [reportId]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  if (error || !report) {
    return (
      <Container maxWidth="lg">
        <Box py={4}>
          <Alert severity="error">
            {error || 'Report not found'}
          </Alert>
        </Box>
      </Container>
    );
  }

  const tabContent = [
    <ReportSummary key="summary" summary={report.summary} metrics={report.metrics} />,
    <IssuesList key="issues" issues={report.all_issues} />,
    <FileMetrics key="files" fileMetrics={report.metrics} />,
    // <QualityTrends key="trends" trends={report.trends} />,
  ];

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Breadcrumbs sx={{ mb: 3 }}>
          <Link to="/">Home</Link>
          <Link to="/analyze">Analysis</Link>
          <Typography color="text.primary">Report</Typography>
        </Breadcrumbs>

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h3" component="h1">
            Analysis Report
          </Typography>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<QuestionAnswer />}
              component={Link}
              to={`/qa/${reportId}`}
            >
              Ask Questions
            </Button>
            <Button
              variant="outlined"
              startIcon={<Share />}
              onClick={() => {
                navigator.clipboard.writeText(window.location.href);
                toast.success('Report URL copied to clipboard');
              }}
            >
              Share
            </Button>
            <Button
              variant="contained"
              startIcon={<GetApp />}
              onClick={() => {
                // TODO: Implement export functionality
                toast.info('Export functionality coming soon');
              }}
            >
              Export
            </Button>
          </Box>
        </Box>

        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            sx={{
              borderBottom: 1,
              borderColor: 'divider'
            }}
          >
            <Tab label="Summary" />
            <Tab label="Issues" />
            <Tab label="File Metrics" />
            {/* <Tab label="Quality Trends" /> */}
          </Tabs>
          
          <Box sx={{ p: 3 }}>
            {tabContent[activeTab]}
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default ReportPage;