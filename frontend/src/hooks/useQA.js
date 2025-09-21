import { useState, useCallback } from 'react';
import { qaService } from '../services/api';
import { storageService } from '../services/storage';

export const useQA = (reportId = null) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const askQuestion = useCallback(async (question, context = null) => {
    setLoading(true);
    setError(null);

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setConversations(prev => [...prev, userMessage]);

    try {
      const response = await qaService.askQuestion(question, reportId, context);
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
        timestamp: new Date().toISOString(),
      };

      setConversations(prev => [...prev, assistantMessage]);

      // Save session
      const sessionId = reportId || 'general';
      storageService.saveQASession(sessionId, {
        reportId,
        conversations: [...conversations, userMessage, assistantMessage],
      });

      return response;
    } catch (err) {
      setError(err);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Sorry, I encountered an error: ${err.message}`,
        timestamp: new Date().toISOString(),
      };
      
      setConversations(prev => [...prev, errorMessage]);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [reportId, conversations]);

  const clearConversation = useCallback(() => {
    setConversations([]);
    setError(null);
  }, []);

  const loadSession = useCallback((sessionId) => {
    const session = storageService.getQASession(sessionId);
    if (session && session.conversations) {
      setConversations(session.conversations);
    }
  }, []);

  return {
    conversations,
    loading,
    error,
    askQuestion,
    clearConversation,
    loadSession,
  };
};