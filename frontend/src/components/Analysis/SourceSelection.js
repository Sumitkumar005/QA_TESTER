import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import { FileUpload, GitHub, Folder } from '@mui/icons-material';
import { toast } from 'react-toastify';
import { analysisService } from '../../services/api';

const SourceSelection = ({ onAnalysisStart }) => {
  const [sourceType, setSourceType] = useState('github');
  const [sourceUrl, setSourceUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [languages, setLanguages] = useState('');
  const [excludePatterns, setExcludePatterns] = useState('');
  const [includeTests, setIncludeTests] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('source_type', sourceType);
      
      if (sourceType === 'github') {
        if (!sourceUrl) {
          toast.error('Please enter a GitHub URL');
          return;
        }
        formData.append('source_path', sourceUrl);
      } else if (sourceType === 'upload') {
        if (!selectedFile) {
          toast.error('Please select a file to upload');
          return;
        }
        formData.append('source_path', selectedFile.name);
        formData.append('file', selectedFile);
      }

      if (languages) {
        formData.append('languages', languages);
      }
      if (excludePatterns) {
        formData.append('exclude_patterns', excludePatterns);
      }
      formData.append('include_tests', includeTests);

      const response = await analysisService.startAnalysis(formData);
      
      toast.success('Analysis started successfully!');
      onAnalysisStart({
        reportId: response.report_id,
        sourceType,
        sourceUrl: sourceType === 'github' ? sourceUrl : selectedFile?.name,
      });
    } catch (error) {
      toast.error(`Failed to start analysis: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (100MB limit)
      const maxSize = 100 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error('File size must be less than 100MB');
        return;
      }

      // Check if it's a code file or archive
      const codeExtensions = [
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
        '.cpp', '.cxx', '.cc', '.c', '.h', '.cs', '.rb', '.php',
        '.kt', '.scala', '.swift', '.m', '.r', '.sql', '.sh', '.bash'
      ];
      const archiveExtensions = ['.zip', '.tar', '.tar.gz', '.tgz'];

      const fileName = file.name.toLowerCase();
      const isCodeFile = codeExtensions.some(ext => fileName.endsWith(ext));
      const isArchive = archiveExtensions.some(ext => fileName.endsWith(ext));

      if (!isCodeFile && !isArchive) {
        toast.error('Please select a code file or archive. Supported: .py, .js, .java, .zip, etc.');
        return;
      }

      setSelectedFile(file);
      toast.success(`Selected ${isCodeFile ? 'code file' : 'archive'}: ${file.name}`);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Select Code Source
      </Typography>

      <form onSubmit={handleSubmit}>
        <Grid container spacing={4}>
          <Grid item xs={12}>
            <FormControl component="fieldset">
              <FormLabel component="legend">Source Type</FormLabel>
              <RadioGroup
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                row
              >
                <FormControlLabel
                  value="github"
                  control={<Radio />}
                  label={
                    <Box display="flex" alignItems="center">
                      <GitHub sx={{ mr: 1 }} />
                      GitHub Repository
                    </Box>
                  }
                />
                <FormControlLabel
                  value="upload"
                  control={<Radio />}
                  label={
                    <Box display="flex" alignItems="center">
                      <FileUpload sx={{ mr: 1 }} />
                      Upload Archive
                    </Box>
                  }
                />
                <FormControlLabel
                  value="local"
                  control={<Radio />}
                  label={
                    <Box display="flex" alignItems="center">
                      <Folder sx={{ mr: 1 }} />
                      Local Path (CLI only)
                    </Box>
                  }
                  disabled
                />
              </RadioGroup>
            </FormControl>
          </Grid>

          {sourceType === 'github' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="GitHub Repository URL"
                placeholder="https://github.com/user/repository"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                required
                helperText="Enter the full GitHub repository URL"
              />
            </Grid>
          )}

          {sourceType === 'upload' && (
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Upload Code File or Archive
                  </Typography>
                  <input
                    type="file"
                    accept=".py,.js,.jsx,.ts,.tsx,.java,.go,.rs,.cpp,.cxx,.cc,.c,.h,.cs,.rb,.php,.kt,.scala,.swift,.m,.r,.sql,.sh,.bash,.zip,.tar.gz,.tgz,.tar"
                    onChange={handleFileChange}
                    style={{ marginBottom: '16px' }}
                  />
                  {selectedFile && (
                    <Box mt={2}>
                      <Chip
                        label={`${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(2)} MB)`}
                        color="primary"
                      />
                    </Box>
                  )}
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    <strong>Supported:</strong>
                    <br />
                    📄 <strong>Code files:</strong> .py, .js, .ts, .java, .go, .rs, .cpp, .c, .cs, .rb, .php, etc.
                    <br />
                    📦 <strong>Archives:</strong> .zip, .tar.gz, .tgz, .tar (Max: 100MB)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Languages to Analyze"
              placeholder="python, javascript, java"
              value={languages}
              onChange={(e) => setLanguages(e.target.value)}
              helperText="Comma-separated list (leave empty for all supported)"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Exclude Patterns"
              placeholder="*.test.js, __pycache__"
              value={excludePatterns}
              onChange={(e) => setExcludePatterns(e.target.value)}
              helperText="Comma-separated patterns to exclude"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Radio
                  checked={includeTests}
                  onChange={(e) => setIncludeTests(e.target.checked)}
                />
              }
              label="Include test files in analysis"
            />
          </Grid>

          <Grid item xs={12}>
            <Alert severity="info">
              <Typography variant="body2">
                The analysis will examine your code for security vulnerabilities, performance issues,
                code quality problems, complexity concerns, and documentation gaps.
                This process may take a few minutes depending on the size of your codebase.
              </Typography>
            </Alert>
          </Grid>

          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Starting Analysis...' : 'Start Analysis'}
            </Button>
          </Grid>
        </Grid>
      </form>
    </Box>
  );
};

export default SourceSelection;