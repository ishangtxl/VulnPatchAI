import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Snackbar,
  Tooltip,
} from '@mui/material';
import {
  Add,
  Download,
  Visibility,
  Assessment,
  Delete,
} from '@mui/icons-material';
import { reportAPI, scanAPI } from '../services/api';
import { Report, Scan } from '../types';

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [generateDialog, setGenerateDialog] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<Report | null>(null);
  const [deleting, setDeleting] = useState(false);
  
  // Form state
  const [selectedScanId, setSelectedScanId] = useState<number | ''>('');
  const [reportType, setReportType] = useState<'executive' | 'technical'>('executive');
  const [reportFormat, setReportFormat] = useState<'html' | 'pdf'>('html');

  const fetchReports = async () => {
    try {
      setLoading(true);
      const [reportsData, scansData] = await Promise.all([
        reportAPI.getReports(),
        scanAPI.getHistory(),
      ]);
      setReports(reportsData);
      setScans(scansData.filter(scan => scan.status === 'completed'));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerateReport = async () => {
    if (!selectedScanId) return;

    try {
      setGenerating(true);
      const report = await reportAPI.generate({
        scan_id: selectedScanId as number,
        report_type: reportType,
        format: reportFormat,
      });
      setReports(prev => [report, ...prev]);
      setGenerateDialog(false);
      setSelectedScanId('');
      setSuccess(`Report "${report.title}" generated successfully!`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = async (reportId: number) => {
    try {
      const report = reports.find(r => r.id === reportId);
      const blob = await reportAPI.downloadReport(reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const extension = report?.format || 'html';
      a.download = `${report?.title?.replace(/[^a-zA-Z0-9]/g, '_') || `report_${reportId}`}.${extension}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download report');
    }
  };

  const handleViewReport = async (reportId: number) => {
    try {
      const report = await reportAPI.getReport(reportId);
      setSelectedReport(report);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load report');
    }
  };

  const handleDeleteClick = (report: Report) => {
    setReportToDelete(report);
    setDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    if (!reportToDelete) return;

    try {
      setDeleting(true);
      await reportAPI.deleteReport(reportToDelete.id);
      setReports(prev => prev.filter(r => r.id !== reportToDelete.id));
      setDeleteDialog(false);
      setReportToDelete(null);
      setSuccess(`Report "${reportToDelete.title}" deleted successfully!`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete report');
    } finally {
      setDeleting(false);
    }
  };

  const getReportTypeColor = (type: string) => {
    return type === 'executive' ? 'primary' : 'secondary';
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf':
        return '📄';
      case 'html':
        return '🌐';
      case 'json':
        return '📊';
      default:
        return '📋';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Reports
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setGenerateDialog(true)}
          disabled={scans.length === 0}
        >
          Generate Report
        </Button>
      </Box>


      {scans.length === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          No completed scans available. Upload and process a scan first to generate reports.
        </Alert>
      )}

      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Format</TableCell>
                  <TableCell>Generated</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {report.title || `Report ${report.id}`}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={report.report_type}
                        color={getReportTypeColor(report.report_type) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <span>{getFormatIcon(report.format)}</span>
                        <Chip
                          label={report.format.toUpperCase()}
                          variant="outlined"
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      {new Date(report.generated_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Preview Report">
                        <IconButton
                          onClick={() => handleViewReport(report.id)}
                          color="primary"
                          size="small"
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download Report">
                        <IconButton
                          onClick={() => handleDownloadReport(report.id)}
                          color="secondary"
                          size="small"
                        >
                          <Download />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Report">
                        <IconButton
                          onClick={() => handleDeleteClick(report)}
                          color="error"
                          size="small"
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {reports.length === 0 && (
            <Box textAlign="center" py={4}>
              <Assessment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No reports generated yet
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Generate your first report from a completed scan
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Generate Report Dialog */}
      <Dialog
        open={generateDialog}
        onClose={() => setGenerateDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Assessment color="primary" />
            Generate New Report
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create a comprehensive vulnerability assessment report with AI-powered analysis and remediation recommendations.
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Select Scan</InputLabel>
                <Select
                  value={selectedScanId}
                  label="Select Scan"
                  onChange={(e) => setSelectedScanId(e.target.value as number)}
                >
                  {scans.map((scan) => (
                    <MenuItem key={scan.id} value={scan.id}>
                      <Box>
                        <Typography variant="body1">{scan.filename}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Uploaded: {new Date(scan.upload_time).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Report Type</InputLabel>
                <Select
                  value={reportType}
                  label="Report Type"
                  onChange={(e) => setReportType(e.target.value as 'executive' | 'technical')}
                >
                  <MenuItem value="executive">
                    <Box>
                      <Typography variant="body2">Executive Summary</Typography>
                      <Typography variant="caption" color="text.secondary">
                        High-level overview for decision makers
                      </Typography>
                    </Box>
                  </MenuItem>
                  <MenuItem value="technical">
                    <Box>
                      <Typography variant="body2">Technical Report</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Detailed analysis with remediation commands
                      </Typography>
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Format</InputLabel>
                <Select
                  value={reportFormat}
                  label="Format"
                  onChange={(e) => setReportFormat(e.target.value as 'html' | 'pdf')}
                >
                  <MenuItem value="html">
                    <Box display="flex" alignItems="center" gap={1}>
                      <span>🌐</span>
                      <Box>
                        <Typography variant="body2">HTML</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Web-viewable format
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                  <MenuItem value="pdf">
                    <Box display="flex" alignItems="center" gap={1}>
                      <span>📄</span>
                      <Box>
                        <Typography variant="body2">PDF</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Professional print-ready document
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          
          {selectedScanId && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>AI Enhancement:</strong> This report will include intelligent vulnerability analysis, 
                business impact assessment, and OS-specific remediation commands powered by advanced LLM technology.
              </Typography>
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialog(false)}>Cancel</Button>
          <Button
            onClick={handleGenerateReport}
            variant="contained"
            disabled={!selectedScanId || generating}
            startIcon={generating ? <CircularProgress size={20} /> : <Assessment />}
          >
            {generating ? 'Generating Report...' : 'Generate Report'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Report Content Dialog */}
      <Dialog
        open={!!selectedReport}
        onClose={() => setSelectedReport(null)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { height: '90vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h6">{selectedReport?.title}</Typography>
              <Box display="flex" gap={1} mt={1}>
                <Chip
                  label={selectedReport?.report_type}
                  color={getReportTypeColor(selectedReport?.report_type || '') as any}
                  size="small"
                />
                <Chip
                  label={`${getFormatIcon(selectedReport?.format || '')} ${selectedReport?.format?.toUpperCase()}`}
                  variant="outlined"
                  size="small"
                />
              </Box>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Generated: {selectedReport?.generated_at && new Date(selectedReport.generated_at).toLocaleString()}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ height: '100%', overflow: 'auto' }}>
          {selectedReport?.format === 'pdf' ? (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" gutterBottom>
                📄 PDF Report Preview
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                PDF reports cannot be previewed directly. Click download to view the full report.
              </Typography>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={() => selectedReport && handleDownloadReport(selectedReport.id)}
                size="large"
              >
                Download PDF Report
              </Button>
            </Box>
          ) : selectedReport?.content ? (
            <Box
              sx={{
                '& h1, & h2, & h3': { 
                  color: 'primary.main', 
                  mt: 3, 
                  mb: 2,
                  borderBottom: '2px solid',
                  borderColor: 'primary.light',
                  pb: 1
                },
                '& h1': { fontSize: '2rem' },
                '& h2': { fontSize: '1.5rem' },
                '& h3': { fontSize: '1.25rem' },
                '& p': { mb: 2, lineHeight: 1.6 },
                '& ul, & ol': { pl: 3, mb: 2 },
                '& li': { mb: 1 },
                '& strong': { color: 'text.primary' },
                '& code': { 
                  backgroundColor: 'grey.100',
                  padding: '2px 6px',
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem'
                },
                '& pre': {
                  backgroundColor: 'grey.100',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: '0.875rem'
                },
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}
              dangerouslySetInnerHTML={{ __html: selectedReport.content }}
            />
          ) : (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="text.secondary">
                No content available for preview.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedReport(null)}>Close</Button>
          <Button
            onClick={() => selectedReport && handleDownloadReport(selectedReport.id)}
            variant="contained"
            startIcon={<Download />}
          >
            Download {selectedReport?.format?.toUpperCase()}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Report Confirmation Dialog */}
      <Dialog
        open={deleteDialog}
        onClose={() => setDeleteDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Delete color="error" />
            Confirm Delete
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to delete the report <strong>"{reportToDelete?.title}"</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This action cannot be undone. The report file will be permanently deleted from the system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            variant="contained"
            disabled={deleting}
            startIcon={deleting ? <CircularProgress size={20} /> : <Delete />}
          >
            {deleting ? 'Deleting...' : 'Delete Report'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess('')}
      >
        <Alert onClose={() => setSuccess('')} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert onClose={() => setError('')} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Reports;