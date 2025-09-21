import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Card,
  CardContent,
  Button,
  Alert,
  Chip,
} from '@mui/material';
import { Cancel, CheckCircle, Error } from '@mui/icons-material';
import { analysisService } from '../../services/api';
import { toast } from 'react-toastify';

const AnalysisProgress = ({ analysisData, onComplete }) => {
  const [status, setStatus] = useState('pending');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!analysisData?.reportId) return;

    const pollStatus = async () => {
      try {
        const response = await analysisService.getAnalysisStatus(analysisData.reportId);
        setStatus(response.status);
        setResult(response);

        if (response.status === 'completed') {
          setProgress(100);
          onComplete(response);
        } else if (response.status === 'failed') {
          setError(response.error_message || 'Analysis failed');
        } else if (response.status === 'in_progress') {
          // Simulate progress based on time (real implementation would track actual progress)
          setProgress(prev => Math.min(prev + 2, 95));
        }
      } catch (err) {
        setError(err.message);
      }
    };

    const interval = setInterval(pollStatus, 2000); // Poll every 2 seconds
    pollStatus(); // Initial call

    return () => clearInterval(interval);
  }, [analysisData?.reportId, onComplete]);

  const handleCancel = async () => {
    try {
      await analysisService.cancelAnalysis(analysisData.reportId);
      setStatus('cancelled');
      toast.info('Analysis cancelled');
    } catch (err) {
      toast.error(`Failed to cancel analysis: ${err.message}`);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
      case 'cancelled':
        return <Error color="error" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'warning';
      case 'in_progress':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analysis in Progress
      </Typography>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">
              Status: <Chip label={status} color={getStatusColor()} icon={getStatusIcon()} />
            </Typography>
            {(status === 'pending' || status === 'in_progress') && (
              <Button
                variant="outlined"
                color="error"
                startIcon={<Cancel />}
                onClick={handleCancel}
              >
                Cancel
              </Button>
            )}
          </Box>

          {analysisData && (
            <Box mb={3}>
              <Typography variant="subtitle2" color="text.secondary">
                Source: {analysisData.sourceType === 'github' ? 'GitHub' : 'Upload'}
              </Typography>
              <Typography variant="body2">
                {analysisData.sourceUrl || 'Uploaded file'}
              </Typography>
            </Box>
          )}

          {(status === 'pending' || status === 'in_progress') && (
            <Box>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{ mb: 2, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary">
                Analyzing code... This may take a few minutes.
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="body2">
                {error}
              </Typography>
            </Alert>
          )}

          {status === 'completed' && result && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Analysis completed successfully! Found {result.issues?.length || 0} issues 
                across {result.file_metrics?.length || 0} files.
              </Typography>
            </Alert>
          )}

          {result && result.metrics && (
            <Box mt={3}>
              <Typography variant="subtitle1" gutterBottom>
                Repository Overview
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                <Chip label={`${result.metrics.total_files} files`} size="small" />
                <Chip label={`${result.metrics.total_lines} lines`} size="small" />
                {result.metrics.languages && Object.entries(result.metrics.languages).map(([lang, count]) => (
                  <Chip key={lang} label={`${lang}: ${count}`} size="small" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalysisProgress;