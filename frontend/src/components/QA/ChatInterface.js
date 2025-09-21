import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Fade,
} from '@mui/material';
import {
  Send,
  Person,
  SmartToy,
  Warning,
  ThumbUp,
  ThumbDown,
} from '@mui/icons-material';
import { formatDateTime } from '../../utils/formatters';

const ChatInterface = ({ 
  conversations = [], 
  loading = false, 
  error = null, 
  onSendMessage,
  onClearChat
}) => {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || loading) return;
    
    onSendMessage(message);
    setMessage('');
  };

  const handleQuickQuestion = (question) => {
    if (!loading) {
      onSendMessage(question);
    }
  };

  const quickQuestions = [
    "What are the most critical security issues?",
    "Which files have the highest complexity?",
    "How can I improve performance?",
    "What are the main maintainability concerns?",
    "Are there any code duplication issues?",
  ];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Messages */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 2,
        maxHeight: '60vh',
        minHeight: '400px'
      }}>
        {conversations.length === 0 && !loading ? (
          <Box textAlign="center" py={4}>
            <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Hi! I'm your AI Code Quality Assistant 🤖
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Ask me anything about your code analysis results, best practices, or how to improve your code quality.
            </Typography>
            
            {/* Quick Questions */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Try asking:
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1} justifyContent="center" maxWidth={600} mx="auto">
                {quickQuestions.map((question, index) => (
                  <Chip
                    key={index}
                    label={question}
                    variant="outlined"
                    size="small"
                    onClick={() => handleQuickQuestion(question)}
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'primary.contrastText'
                      }
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Box>
        ) : (
          <Box>
            {conversations.map((conv, index) => (
              <Fade in={true} key={index} timeout={300} style={{ transitionDelay: `${index * 100}ms` }}>
                <Box
                  sx={{
                    display: 'flex',
                    mb: 3,
                    flexDirection: conv.type === 'user' ? 'row-reverse' : 'row',
                    alignItems: 'flex-start',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: conv.type === 'user' ? 'primary.main' : 
                               conv.type === 'error' ? 'error.main' : 'secondary.main',
                      mx: 1,
                      width: 40,
                      height: 40,
                    }}
                  >
                    {conv.type === 'user' ? <Person /> : 
                     conv.type === 'error' ? <Warning /> : <SmartToy />}
                  </Avatar>
                  
                  <Paper
                    elevation={conv.type === 'user' ? 3 : 1}
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: 
                        conv.type === 'user' ? 'primary.light' : 
                        conv.type === 'error' ? 'error.light' : 'background.paper',
                      color: conv.type === 'user' ? 'primary.contrastText' : 'text.primary',
                    }}
                  >
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
                      {conv.content}
                    </Typography>
                    
                    {/* Sources */}
                    {conv.sources && conv.sources.length > 0 && (
                      <Box mt={1}>
                        <Typography variant="caption" color="text.secondary">
                          📚 Sources: {conv.sources.join(', ')}
                        </Typography>
                      </Box>
                    )}
                    
                    {/* Confidence Score */}
                    {conv.confidence && (
                      <Box mt={1} display="flex" alignItems="center" gap={1}>
                        <Chip
                          label={`${Math.round(conv.confidence * 100)}% confident`}
                          size="small"
                          variant="outlined"
                          color={conv.confidence > 0.7 ? 'success' : 'warning'}
                        />
                      </Box>
                    )}
                    
                    {/* Feedback Buttons for AI responses */}
                    {conv.type === 'assistant' && (
                      <Box mt={1} display="flex" gap={1}>
                        <Button
                          size="small"
                          startIcon={<ThumbUp />}
                          onClick={() => console.log('Positive feedback')}
                          sx={{ minWidth: 'auto', px: 1 }}
                        >
                          Helpful
                        </Button>
                        <Button
                          size="small"
                          startIcon={<ThumbDown />}
                          onClick={() => console.log('Negative feedback')}
                          sx={{ minWidth: 'auto', px: 1 }}
                        >
                          Not helpful
                        </Button>
                      </Box>
                    )}
                    
                    <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                      {formatDateTime(conv.timestamp)}
                    </Typography>
                  </Paper>
                </Box>
              </Fade>
            ))}
            
            {/* Loading indicator */}
            {loading && (
              <Box display="flex" alignItems="center" gap={1} p={2}>
                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                  <SmartToy />
                </Avatar>
                <Paper elevation={1} sx={{ p: 2, flex: 1 }}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <CircularProgress size={20} />
                    <Typography variant="body2">
                      AI is thinking and analyzing your question...
                    </Typography>
                  </Box>
                </Paper>
              </Box>
            )}
            
            {/* Error display */}
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  {error}
                </Typography>
              </Alert>
            )}
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper
        component="form"
        onSubmit={handleSubmit}
        elevation={3}
        sx={{
          p: 2,
          display: 'flex',
          gap: 1,
          alignItems: 'flex-end',
          borderTop: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper',
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask a question about your code..."
          variant="outlined"
          size="small"
          disabled={loading}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            }
          }}
        />
        <Button
          type="submit"
          variant="contained"
          disabled={!message.trim() || loading}
          startIcon={loading ? <CircularProgress size={16} /> : <Send />}
          sx={{ 
            borderRadius: 2,
            px: 3,
            py: 1.5,
            minWidth: 'auto'
          }}
        >
          {loading ? 'Sending...' : 'Send'}
        </Button>
      </Paper>

      {/* Clear Chat Button */}
      {conversations.length > 0 && (
        <Box sx={{ p: 1, textAlign: 'center' }}>
          <Button
            size="small"
            onClick={onClearChat}
            sx={{ opacity: 0.7 }}
          >
            Clear Chat History
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ChatInterface;