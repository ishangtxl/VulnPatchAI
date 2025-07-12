import axios, { AxiosResponse } from 'axios';
import { 
  User, 
  Scan, 
  Vulnerability, 
  Report, 
  DashboardMetrics, 
  TrendData,
  LoginForm,
  RegisterForm,
  ReportGenerateForm,
  AIQueryForm
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (data: LoginForm): Promise<{ access_token: string; token_type: string }> => {
    const formData = new FormData();
    formData.append('username', data.email);
    formData.append('password', data.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  register: async (data: RegisterForm): Promise<User> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },
};

// Scan API
export const scanAPI = {
  upload: async (file: File): Promise<Scan> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/scan/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  getHistory: async (skip = 0, limit = 100): Promise<Scan[]> => {
    const response = await api.get(`/scan/history?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getScan: async (scanId: number): Promise<Scan> => {
    const response = await api.get(`/scan/${scanId}`);
    return response.data;
  },

  deleteScan: async (scanId: number): Promise<void> => {
    await api.delete(`/scan/${scanId}`);
  },
};

// Vulnerability API
export const vulnerabilityAPI = {
  getVulnerabilities: async (params?: {
    scan_id?: number;
    severity?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<Vulnerability[]> => {
    const response = await api.get('/vulnerabilities', { params });
    return response.data;
  },

  getVulnerability: async (vulnId: number): Promise<Vulnerability> => {
    const response = await api.get(`/vulnerabilities/${vulnId}`);
    return response.data;
  },

  updateStatus: async (vulnId: number, status: string): Promise<Vulnerability> => {
    const response = await api.patch(`/vulnerabilities/${vulnId}/status`, { status });
    return response.data;
  },

  addFeedback: async (vulnId: number, feedback: {
    rating: number;
    comment?: string;
    feedback_type?: string;
  }): Promise<void> => {
    await api.post(`/vulnerabilities/${vulnId}/feedback`, feedback);
  },
  deleteVulnerability: async (vulnId: number): Promise<void> => {
    await api.delete(`/vulnerabilities/${vulnId}`);
  },
  refreshCVEData: async (vulnId: number): Promise<Vulnerability> => {
    const response = await api.post(`/vulnerabilities/${vulnId}/refresh-cve`);
    return response.data;
  },

  getVulnerabilitiesByScans: async (): Promise<any[]> => {
    const response = await api.get('/vulnerabilities/scans');
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getMetrics: async (): Promise<DashboardMetrics> => {
    const response = await api.get('/dashboard/metrics');
    return response.data;
  },

  getTrends: async (days = 30): Promise<TrendData> => {
    const response = await api.get(`/dashboard/trends?days=${days}`);
    return response.data;
  },
};

// Report API
export const reportAPI = {
  generate: async (data: ReportGenerateForm): Promise<Report> => {
    const response = await api.post('/reports/generate', data);
    return response.data;
  },

  getReports: async (skip = 0, limit = 100): Promise<Report[]> => {
    const response = await api.get(`/reports?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getReport: async (reportId: number): Promise<Report> => {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
  },

  downloadReport: async (reportId: number): Promise<Blob> => {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  deleteReport: async (reportId: number): Promise<void> => {
    await api.delete(`/reports/${reportId}`);
  },
};

// AI API
export const aiAPI = {
  query: async (data: AIQueryForm): Promise<{ query: string; response: string; timestamp?: string; conversation_id?: string }> => {
    const response = await api.post('/ai/query', data);
    return response.data;
  },

  analyzeScan: async (scanId: number): Promise<{
    scan_id: number;
    summary: string;
    key_findings: string[];
    recommendations: string[];
    risk_score: number;
    generated_at: string;
  }> => {
    const response = await api.post('/ai/analyze', { scan_id: scanId });
    return response.data;
  },
};

// Conversation API
export const conversationAPI = {
  getConversations: async (): Promise<any[]> => {
    const response = await api.get('/conversation/conversations');
    return response.data;
  },

  getConversationMessages: async (conversationId: string): Promise<any[]> => {
    const response = await api.get(`/conversation/conversations/${conversationId}/messages`);
    return response.data;
  },

  getConversation: async (conversationId: string): Promise<any> => {
    const response = await api.get(`/conversation/conversations/${conversationId}`);
    return response.data;
  },

  updateConversationTitle: async (conversationId: string, title: string): Promise<void> => {
    await api.patch(`/conversation/conversations/${conversationId}/title`, { title });
  },

  deleteConversation: async (conversationId: string): Promise<void> => {
    await api.delete(`/conversation/conversations/${conversationId}`);
  },

  archiveConversation: async (conversationId: string): Promise<void> => {
    await api.patch(`/conversation/conversations/${conversationId}/archive`);
  },

  getUserPreferences: async (): Promise<any> => {
    const response = await api.get('/conversation/preferences');
    return response.data;
  },

  updateUserPreferences: async (preferences: any): Promise<void> => {
    await api.patch('/conversation/preferences', preferences);
  },

  updateMessageFeedback: async (messageId: number, feedback: {
    rating?: number;
    was_helpful?: boolean;
    correction?: string;
  }): Promise<void> => {
    await api.post(`/conversation/messages/${messageId}/feedback`, feedback);
  },
};

// Admin API
export const adminAPI = {
  getFeedbackOverview: async (days: number = 30): Promise<any> => {
    const response = await api.get(`/admin/feedback/overview?days=${days}`);
    return response.data;
  },

  getDetailedFeedback: async (filters: {
    page?: number;
    page_size?: number;
    feedback_type?: string;
    analysis_type?: string;
    min_rating?: string;
    max_rating?: string;
    user_id?: number;
    days?: number;
  }): Promise<any> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        params.append(key, value.toString());
      }
    });
    
    const response = await api.get(`/admin/feedback/detailed?${params.toString()}`);
    return response.data;
  },

  getAdvancedAnalytics: async (): Promise<any> => {
    const response = await api.get('/admin/feedback/analytics/advanced');
    return response.data;
  },

  refreshLearning: async (analysisType?: string): Promise<any> => {
    const params = analysisType ? `?analysis_type=${analysisType}` : '';
    const response = await api.post(`/admin/learning/manual-refresh${params}`);
    return response.data;
  },

  applyLearningAllTypes: async (): Promise<any> => {
    const response = await api.post('/admin/learning/apply-all');
    return response.data;
  },

  deleteFeedback: async (feedbackId: number): Promise<any> => {
    const response = await api.delete(`/admin/feedback/${feedbackId}`);
    return response.data;
  },

  getSystemStatus: async (): Promise<any> => {
    const response = await api.get('/admin/system/status');
    return response.data;
  },

  exportFeedbackData: async (days: number = 30, format: string = 'json'): Promise<any> => {
    const response = await api.get(`/admin/export/feedback?days=${days}&format=${format}`);
    return response.data;
  }
};

export default api;