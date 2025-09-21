const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Remove content-type for FormData
    if (options.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

const apiClient = new ApiClient();

// Analysis Service
export const analysisService = {
  async startAnalysis(formData) {
    return apiClient.post('/api/v1/analyze', formData);
  },

  async getAnalysisStatus(reportId) {
    return apiClient.get(`/api/v1/analyze/${reportId}/status`);
  },

  async cancelAnalysis(reportId) {
    return apiClient.delete(`/api/v1/analyze/${reportId}`);
  },

  async getSupportedLanguages() {
    return apiClient.get('/api/v1/analyze/supported-languages');
  },
};

// Reports Service
export const reportsService = {
  async getReport(reportId, detailed = true) {
    return apiClient.get(`/api/v1/report/${reportId}?detailed=${detailed}`);
  },
};

// Q&A Service
export const qaService = {
  async askQuestion(question, reportId = null, context = null) {
    return apiClient.post('/api/v1/ask', {
      question,
      report_id: reportId,
      context,
    });
  },
};

// Health Check
export const healthService = {
  async checkHealth() {
    return apiClient.get('/health');
  },
};

export default apiClient;