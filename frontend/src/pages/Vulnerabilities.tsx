import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  CircularProgress,
  Alert,
  Link,
} from '@mui/material';
import {
  Visibility,
  Edit,
  Feedback,
  OpenInNew,
  Delete,
  Refresh,
} from '@mui/icons-material';
import { vulnerabilityAPI } from '../services/api';
import { Vulnerability } from '../types';
import CommandBlock from '../components/CommandBlock';

const Vulnerabilities: React.FC = () => {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedVuln, setSelectedVuln] = useState<Vulnerability | null>(null);
  const [feedbackDialog, setFeedbackDialog] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [vulnToDelete, setVulnToDelete] = useState<Vulnerability | null>(null);
  
  // Filters
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchFilter, setSearchFilter] = useState('');

  const fetchVulnerabilities = async () => {
    try {
      setLoading(true);
      const data = await vulnerabilityAPI.getVulnerabilities({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
      });
      setVulnerabilities(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load vulnerabilities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVulnerabilities();
  }, [severityFilter, statusFilter]);

  const handleStatusUpdate = async (vulnId: number, newStatus: string) => {
    try {
      await vulnerabilityAPI.updateStatus(vulnId, newStatus);
      setVulnerabilities(vulns =>
        vulns.map(v => v.id === vulnId ? { ...v, status: newStatus as any } : v)
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update status');
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!selectedVuln || !feedbackRating) return;

    try {
      await vulnerabilityAPI.addFeedback(selectedVuln.id, {
        rating: feedbackRating,
        comment: feedbackComment,
        feedback_type: 'recommendation',
      });
      setFeedbackDialog(false);
      setFeedbackRating(null);
      setFeedbackComment('');
      setSelectedVuln(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit feedback');
    }
  };

  const handleDeleteVulnerability = async () => {
    if (!vulnToDelete) return;

    try {
      await vulnerabilityAPI.deleteVulnerability(vulnToDelete.id);
      setVulnerabilities(vulns => vulns.filter(v => v.id !== vulnToDelete.id));
      setDeleteDialog(false);
      setVulnToDelete(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete vulnerability');
    }
  };

  const handleRefreshCVE = async (vulnId: number) => {
    try {
      const updatedVuln = await vulnerabilityAPI.refreshCVEData(vulnId);
      setVulnerabilities(vulns =>
        vulns.map(v => v.id === vulnId ? updatedVuln : v)
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to refresh CVE data');
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'error';
      case 'patched':
        return 'success';
      case 'ignored':
        return 'default';
      case 'false_positive':
        return 'info';
      default:
        return 'default';
    }
  };

  const filteredVulnerabilities = vulnerabilities.filter(vuln =>
    searchFilter === '' ||
    vuln.service_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    vuln.description?.toLowerCase().includes(searchFilter.toLowerCase())
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Vulnerabilities
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={severityFilter}
                  label="Severity"
                  onChange={(e) => setSeverityFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="Critical">Critical</MenuItem>
                  <MenuItem value="High">High</MenuItem>
                  <MenuItem value="Medium">Medium</MenuItem>
                  <MenuItem value="Low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="patched">Patched</MenuItem>
                  <MenuItem value="ignored">Ignored</MenuItem>
                  <MenuItem value="false_positive">False Positive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={12} md={6}>
              <TextField
                fullWidth
                label="Search"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="Search by service name or description..."
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Vulnerabilities Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Service</TableCell>
                  <TableCell>Port</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>CVE ID</TableCell>
                  <TableCell>CVSS Score</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredVulnerabilities.map((vuln) => (
                  <TableRow key={vuln.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {vuln.service_name}
                      </Typography>
                      {vuln.service_version && (
                        <Typography variant="caption" color="textSecondary">
                          v{vuln.service_version}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{vuln.port}</TableCell>
                    <TableCell>
                      <Chip
                        label={vuln.severity || 'Unknown'}
                        color={getSeverityColor(vuln.severity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {vuln.cve_id ? (
                        <Link
                          href={`https://nvd.nist.gov/vuln/detail/${vuln.cve_id}`}
                          target="_blank"
                          rel="noopener"
                        >
                          {vuln.cve_id}
                          <OpenInNew sx={{ ml: 0.5, fontSize: 14 }} />
                        </Link>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                    <TableCell>
                      {vuln.cvss_score ? vuln.cvss_score.toFixed(1) : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <FormControl size="small" sx={{ minWidth: 120 }}>
                        <Select
                          value={vuln.status}
                          onChange={(e) => handleStatusUpdate(vuln.id, e.target.value)}
                        >
                          <MenuItem value="open">Open</MenuItem>
                          <MenuItem value="patched">Patched</MenuItem>
                          <MenuItem value="ignored">Ignored</MenuItem>
                          <MenuItem value="false_positive">False Positive</MenuItem>
                        </Select>
                      </FormControl>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        onClick={() => setSelectedVuln(vuln)}
                        color="primary"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton
                        onClick={() => {
                          setSelectedVuln(vuln);
                          setFeedbackDialog(true);
                        }}
                        color="secondary"
                      >
                        <Feedback />
                      </IconButton>
                      <IconButton
                        onClick={() => handleRefreshCVE(vuln.id)}
                        color="info"
                        title="Refresh CVE Data"
                      >
                        <Refresh />
                      </IconButton>
                      <IconButton
                        onClick={() => {
                          setVulnToDelete(vuln);
                          setDeleteDialog(true);
                        }}
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {filteredVulnerabilities.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary">
                No vulnerabilities found
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Vulnerability Details Dialog */}
      <Dialog
        open={!!selectedVuln && !feedbackDialog}
        onClose={() => setSelectedVuln(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Vulnerability Details</DialogTitle>
        <DialogContent>
          {selectedVuln && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedVuln.service_name} {selectedVuln.service_version}
              </Typography>
              
              {selectedVuln.scan && (
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  <strong>Source File:</strong> {selectedVuln.scan.original_filename || selectedVuln.scan.filename}
                </Typography>
              )}
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    <strong>Port:</strong> {selectedVuln.port}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    <strong>Protocol:</strong> {selectedVuln.protocol}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    <strong>Severity:</strong> 
                    <Chip
                      label={selectedVuln.severity || 'Unknown'}
                      color={getSeverityColor(selectedVuln.severity) as any}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    <strong>CVSS Score:</strong> {selectedVuln.cvss_score ? selectedVuln.cvss_score.toFixed(1) : 'N/A'}
                  </Typography>
                </Grid>
                {selectedVuln.cve_id && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>CVE ID:</strong> 
                      <Link
                        href={`https://nvd.nist.gov/vuln/detail/${selectedVuln.cve_id}`}
                        target="_blank"
                        rel="noopener"
                        sx={{ ml: 1 }}
                      >
                        {selectedVuln.cve_id}
                        <OpenInNew sx={{ ml: 0.5, fontSize: 14 }} />
                      </Link>
                    </Typography>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    <strong>Status:</strong> 
                    <Chip
                      label={selectedVuln.status.replace('_', ' ').toUpperCase()}
                      color={getStatusColor(selectedVuln.status) as any}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Grid>
              </Grid>

              {selectedVuln.description && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Description
                  </Typography>
                  <Typography variant="body2">
                    {selectedVuln.description}
                  </Typography>
                </Box>
              )}

              {selectedVuln.recommendation && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Recommendations
                  </Typography>
                  <Box sx={{ pl: 1 }}>
                    {selectedVuln.recommendation.split(/\d+\.\s|\*\s|\n\s*\*/).filter(item => item.trim()).map((item, index) => {
                      const cleanItem = item.trim();
                      if (!cleanItem) return null;
                      
                      // Check if it's a main recommendation (contains **)
                      const isMainPoint = cleanItem.includes('**');
                      
                      if (isMainPoint) {
                        // Extract the main point title and description
                        const parts = cleanItem.split('**');
                        const title = parts[1] || '';
                        const description = parts.slice(2).join('').replace(/^\s*:?\s*/, '');
                        
                        return (
                          <Box key={index} sx={{ mb: 1.5 }}>
                            <Typography variant="body2" fontWeight="bold" color="primary">
                              • {title}
                            </Typography>
                            {description && (
                              <Typography variant="body2" sx={{ ml: 2, color: 'text.secondary' }}>
                                {description}
                              </Typography>
                            )}
                          </Box>
                        );
                      } else {
                        // Regular bullet point
                        return (
                          <Typography key={index} variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}>
                            <span style={{ marginRight: '8px', color: '#1976d2' }}>•</span>
                            <span>{cleanItem}</span>
                          </Typography>
                        );
                      }
                    })}
                  </Box>
                </Box>
              )}

              {selectedVuln.remediation_commands && selectedVuln.remediation_commands.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Terminal Commands
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    Execute these commands to remediate the vulnerability. Always review commands before execution.
                  </Typography>
                  {selectedVuln.remediation_commands.map((command, index) => (
                    <CommandBlock key={index} command={command} index={index} />
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedVuln(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Feedback Dialog */}
      <Dialog
        open={feedbackDialog}
        onClose={() => setFeedbackDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Provide Feedback</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography variant="body2" gutterBottom>
              How helpful was the AI recommendation for this vulnerability?
            </Typography>
            <Rating
              value={feedbackRating}
              onChange={(_, newValue) => setFeedbackRating(newValue)}
              size="large"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Additional Comments"
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
              placeholder="Share your thoughts on the recommendation..."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialog(false)}>Cancel</Button>
          <Button
            onClick={handleFeedbackSubmit}
            variant="contained"
            disabled={!feedbackRating}
          >
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog}
        onClose={() => setDeleteDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this vulnerability?
          </Typography>
          {vulnToDelete && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="body2" fontWeight="bold">
                {vulnToDelete.service_name} {vulnToDelete.service_version}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Port: {vulnToDelete.port} • Severity: {vulnToDelete.severity}
              </Typography>
              {vulnToDelete.cve_id && (
                <Typography variant="body2" color="textSecondary">
                  CVE: {vulnToDelete.cve_id}
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteVulnerability}
            variant="contained"
            color="error"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Vulnerabilities;