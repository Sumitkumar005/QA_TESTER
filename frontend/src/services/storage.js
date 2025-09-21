export const storageService = {
  // Store recent analyses
  saveRecentAnalysis(reportId, metadata) {
    const recent = this.getRecentAnalyses();
    const newAnalysis = {
      reportId,
      ...metadata,
      timestamp: new Date().toISOString(),
    };
    
    // Add to beginning and limit to 10 recent items
    const updated = [newAnalysis, ...recent.filter(a => a.reportId !== reportId)].slice(0, 10);
    localStorage.setItem('recentAnalyses', JSON.stringify(updated));
  },

  getRecentAnalyses() {
    try {
      const stored = localStorage.getItem('recentAnalyses');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  },

  removeRecentAnalysis(reportId) {
    const recent = this.getRecentAnalyses();
    const filtered = recent.filter(a => a.reportId !== reportId);
    localStorage.setItem('recentAnalyses', JSON.stringify(filtered));
  },

  // Store Q&A sessions
  saveQASession(sessionId, data) {
    const sessions = this.getQASessions();
    sessions[sessionId] = {
      ...data,
      lastUpdated: new Date().toISOString(),
    };
    
    // Keep only last 50 sessions
    const sessionKeys = Object.keys(sessions);
    if (sessionKeys.length > 50) {
      const sortedKeys = sessionKeys.sort((a, b) => 
        new Date(sessions[b].lastUpdated) - new Date(sessions[a].lastUpdated)
      );
      const toKeep = sortedKeys.slice(0, 50);
      const filtered = {};
      toKeep.forEach(key => filtered[key] = sessions[key]);
      localStorage.setItem('qaSessions', JSON.stringify(filtered));
    } else {
      localStorage.setItem('qaSessions', JSON.stringify(sessions));
    }
  },

  getQASessions() {
    try {
      const stored = localStorage.getItem('qaSessions');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  },

  getQASession(sessionId) {
    const sessions = this.getQASessions();
    return sessions[sessionId] || null;
  },

  // User preferences
  savePreferences(preferences) {
    localStorage.setItem('userPreferences', JSON.stringify(preferences));
  },

  getPreferences() {
    try {
      const stored = localStorage.getItem('userPreferences');
      return stored ? JSON.parse(stored) : {
        theme: 'dark',
        defaultLanguages: [],
        includeTests: true,
      };
    } catch {
      return {
        theme: 'dark',
        defaultLanguages: [],
        includeTests: true,
      };
    }
  },
};