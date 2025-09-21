import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
} from '@mui/material';
import SourceSelection from '../components/Analysis/SourceSelection';
import AnalysisProgress from '../components/Analysis/AnalysisProgress';
import AnalysisResults from '../components/Analysis/AnalysisResults';

const steps = ['Select Source', 'Run Analysis', 'View Results'];

const AnalysisPage = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [analysisData, setAnalysisData] = useState(null);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleAnalysisStart = (data) => {
    setAnalysisData(data);
    handleNext();
  };

  const handleAnalysisComplete = (results) => {
    setAnalysisData({ ...analysisData, results });
    handleNext();
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return <SourceSelection onAnalysisStart={handleAnalysisStart} />;
      case 1:
        return (
          <AnalysisProgress
            analysisData={analysisData}
            onComplete={handleAnalysisComplete}
          />
        );
      case 2:
        return <AnalysisResults results={analysisData?.results} />;
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography variant="h3" component="h1" gutterBottom textAlign="center">
          Code Analysis
        </Typography>
        
        <Paper sx={{ p: 3, mt: 4 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box mt={3}>
            {getStepContent(activeStep)}
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              variant="outlined"
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={activeStep === steps.length - 1}
            >
              {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default AnalysisPage;