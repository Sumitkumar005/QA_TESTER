// frontend/src/utils/formatters.js
import React from 'react';
import {
  Security,
  Speed,
  BugReport,
  Build,
  Assessment,
  Description,
  Warning,
} from '@mui/icons-material';

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

export const formatDuration = (startTime, endTime) => {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const duration = Math.abs(end - start) / 1000; // seconds
  
  if (duration < 60) {
    return `${Math.round(duration)}s`;
  } else if (duration < 3600) {
    return `${Math.round(duration / 60)}m`;
  } else {
    return `${Math.round(duration / 3600)}h`;
  }
};

export const getSeverityColor = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return '#f44336'; // red
    case 'high':
      return '#ff9800'; // orange
    case 'medium':
      return '#ffc107'; // yellow
    case 'low':
      return '#4caf50'; // green
    case 'info':
      return '#2196f3'; // blue
    default:
      return '#9e9e9e'; // grey
  }
};

// Return React components instead of emoji strings
export const getCategoryIcon = (category) => {
  const iconMap = {
    security: <Security />,
    performance: <Speed />,
    code_quality: <BugReport />,
    maintainability: <Build />,
    testing: <Assessment />,
    documentation: <Description />,
    complexity: <Build />,
    duplication: <Description />,
  };
  
  return iconMap[category?.toLowerCase()] || <Warning />;
};

export const getCategoryColor = (category) => {
  const colors = {
    security: 'error',
    performance: 'warning',
    code_quality: 'info',
    maintainability: 'primary',
    testing: 'secondary',
    documentation: 'default',
    complexity: 'warning',
    duplication: 'info',
  };
  return colors[category?.toLowerCase()] || 'default';
};

export const getQualityScoreColor = (score) => {
  if (score >= 80) return '#4caf50'; // green
  if (score >= 60) return '#ff9800'; // orange  
  return '#f44336'; // red
};

export const getScoreGrade = (score) => {
  if (score >= 90) return 'A+';
  if (score >= 80) return 'A';
  if (score >= 70) return 'B';
  if (score >= 60) return 'C';
  if (score >= 50) return 'D';
  return 'F';
};