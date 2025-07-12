// API Response Types
export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Scan {
  id: number;
  user_id: number;
  filename: string;
  original_filename?: string;
  status: 'processing' | 'completed' | 'failed';
  upload_time: string;
  processed_at?: string;
  file_size?: number;
  parsed_data?: any;
  error_message?: string;
  created_at: string;
  target_hosts?: string[];
}

export interface ScanInfo {
  id: number;
  filename: string;
  original_filename: string;
}

export interface RemediationCommand {
  title: string;
  command: string;
  os: string;
  description?: string;
  requires_sudo: boolean;
  is_destructive: boolean;
}

export interface Vulnerability {
  id: number;
  scan_id: number;
  service_name: string;
  service_version?: string;
  port?: number;
  protocol?: string;
  cve_id?: string;
  cvss_score?: number;
  severity?: 'Critical' | 'High' | 'Medium' | 'Low';
  description?: string;
  recommendation?: string;
  remediation_commands?: RemediationCommand[];
  status: 'open' | 'patched' | 'ignored' | 'false_positive';
  created_at: string;
  updated_at?: string;
  scan?: ScanInfo;
}

export interface Report {
  id: number;
  scan_id: number;
  user_id: number;
  report_type: 'executive' | 'technical';
  title: string;
  description?: string;
  content?: string;
  format: 'html' | 'pdf' | 'json';
  file_path?: string;
  status: 'generating' | 'completed' | 'failed';
  created_at: string;
  generated_at: string;
}

export interface DashboardMetrics {
  total_scans: number;
  vulnerabilities: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  patch_completion_rate: number;
  recent_scans: number;
  avg_cvss_score: number;
}

export interface TrendData {
  vulnerability_trends: Array<{ date: string; value: number }>;
  scan_trends: Array<{ date: string; value: number }>;
  severity_distribution: Record<string, number>;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  full_name?: string;
}

export interface ScanUploadForm {
  file: File;
}

export interface ReportGenerateForm {
  scan_id: number;
  report_type: 'executive' | 'technical';
  format: 'html' | 'pdf';
}

export interface AIQueryForm {
  query: string;
  context?: any;
}

// API Response Wrappers
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Error Types
export interface ApiError {
  detail: string;
  status_code: number;
}