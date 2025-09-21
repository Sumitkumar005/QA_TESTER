import { useState, useEffect, useCallback } from 'react';
import { analysisService } from '../services/api';
import { storageService } from '../services/storage';

export const useAnalysis = (reportId) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = useCallback(async (id = reportId) => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const result = await analysisService.getAnalysisStatus(id);
      setAnalysis(result);

      // Save to recent analyses if completed
      if (result.status === 'completed') {
        storageService.saveRecentAnalysis(id, {
          sourceType: result.source_info?.type || 'unknown',
          sourcePath: result.source_info?.path || 'unknown',
          completedAt: result.completed_at,
          issuesCount: result.issues?.length || 0,
        });
      }

      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  useEffect(() => {
    if (reportId) {
      fetchAnalysis(reportId);
    }
  }, [reportId, fetchAnalysis]);

  const startAnalysis = async (formData) => {
    setLoading(true);
    setError(null);

    try {
      const result = await analysisService.startAnalysis(formData);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const cancelAnalysis = async (id = reportId) => {
    try {
      await analysisService.cancelAnalysis(id);
      if (id === reportId) {
        await fetchAnalysis(id); // Refresh status
      }
    } catch (err) {
      setError(err);
      throw err;
    }
  };

  return {
    analysis,
    loading,
    error,
    fetchAnalysis,
    startAnalysis,
    cancelAnalysis,
    refetch: () => fetchAnalysis(reportId),
  };
};