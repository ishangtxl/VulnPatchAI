import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Autocomplete,
  Divider,
  Alert,
  CircularProgress,
  Link,
  Pagination,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore,
  FilterList,
  Clear,
  Visibility,
  Download,
  OpenInNew,
  TuneOutlined,
} from '@mui/icons-material';
import { vulnerabilityAPI, scanAPI, reportAPI } from '../services/api';
import { Vulnerability, Scan, Report } from '../types';

interface SearchFilters {
  dateFrom: Date | null;
  dateTo: Date | null;
  severity: string[];
  status: string[];
  categories: string[];
  hosts: string[];
  ports: string[];
}

interface SearchResult {
  vulnerabilities: Vulnerability[];
  scans: Scan[];
  reports: Report[];
  totalResults: number;
}

const Search: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    dateFrom: null,
    dateTo: null,
    severity: [],
    status: [],
    categories: [],
    hosts: [],
    ports: [],
  });
  const [results, setResults] = useState<SearchResult>({
    vulnerabilities: [],
    scans: [],
    reports: [],
    totalResults: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Options for autocomplete filters
  const severityOptions = ['Critical', 'High', 'Medium', 'Low'];
  const statusOptions = ['Open', 'Patched', 'Ignored', 'False Positive'];
  const categoryOptions = ['Web Application', 'Network', 'Database', 'Operating System', 'SSL/TLS'];

  const performSearch = async () => {
    if (!searchQuery.trim() && Object.values(filters).every(f => 
      f === null || (Array.isArray(f) && f.length === 0)
    )) {
      setError('Please enter a search query or apply filters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const searchParams = {
        query: searchQuery,
        skip: (page - 1) * pageSize,
        limit: pageSize,
        ...filters,
      };

      // Parallel search across all data types
      const [vulnResults, scanResults, reportResults] = await Promise.all([
        vulnerabilityAPI.getVulnerabilities({
          ...searchParams,
          severity: filters.severity.length > 0 ? filters.severity.join(',') : undefined,
          status: filters.status.length > 0 ? filters.status.join(',') : undefined,
        }),
        scanAPI.getHistory(),
        reportAPI.getReports(),
      ]);

      // Filter results based on search query
      const filteredScans = scanResults.filter(scan => 
        !searchQuery || 
        scan.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scan.target_hosts?.some(host => host.toLowerCase().includes(searchQuery.toLowerCase()))
      );

      const filteredReports = reportResults.filter(report =>
        !searchQuery ||
        report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );

      setResults({
        vulnerabilities: vulnResults,
        scans: filteredScans,
        reports: filteredReports,
        totalResults: vulnResults.length + filteredScans.length + filteredReports.length,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({
      dateFrom: null,
      dateTo: null,
      severity: [],
      status: [],
      categories: [],
      hosts: [],
      ports: [],
    });
    setSearchQuery('');
    setResults({
      vulnerabilities: [],
      scans: [],
      reports: [],
      totalResults: 0,
    });
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open': return 'error';
      case 'patched': return 'success';
      case 'ignored': return 'default';
      case 'false_positive': return 'info';
      default: return 'default';
    }
  };

  const tabLabels = [
    `All Results (${results.totalResults})`,
    `Vulnerabilities (${results.vulnerabilities.length})`,
    `Scans (${results.scans.length})`,
    `Reports (${results.reports.length})`,
  ];

  return (
    <Box>
        <Typography variant="h4" gutterBottom>
          Advanced Search
        </Typography>

        {/* Search Bar */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" gap={2} alignItems="center">
              <TextField
                fullWidth
                placeholder="Search vulnerabilities, scans, reports..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && performSearch()}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
              />
              <Button
                variant="contained"
                onClick={performSearch}
                disabled={loading}
                sx={{ minWidth: 100 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Search'}
              </Button>
              <IconButton
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                color={showAdvancedFilters ? 'primary' : 'default'}
              >
                <TuneOutlined />
              </IconButton>
            </Box>
          </CardContent>
        </Card>

        {/* Advanced Filters */}
        {showAdvancedFilters && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" display="flex" alignItems="center">
                  <FilterList sx={{ mr: 1 }} />
                  Advanced Filters
                </Typography>
                <Button startIcon={<Clear />} onClick={clearFilters}>
                  Clear All
                </Button>
              </Box>

              <Grid container spacing={3}>
                {/* Date Range */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Date Range
                  </Typography>
                  <Box display="flex" gap={2}>
                    <TextField
                      label="From"
                      type="date"
                      size="small"
                      value={filters.dateFrom ? filters.dateFrom.toISOString().split('T')[0] : ''}
                      onChange={(e) => setFilters(prev => ({ 
                        ...prev, 
                        dateFrom: e.target.value ? new Date(e.target.value) : null 
                      }))}
                      InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                      label="To"
                      type="date"
                      size="small"
                      value={filters.dateTo ? filters.dateTo.toISOString().split('T')[0] : ''}
                      onChange={(e) => setFilters(prev => ({ 
                        ...prev, 
                        dateTo: e.target.value ? new Date(e.target.value) : null 
                      }))}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Box>
                </Grid>

                {/* Severity Filter */}
                <Grid item xs={12} md={6}>
                  <Autocomplete
                    multiple
                    options={severityOptions}
                    value={filters.severity}
                    onChange={(_, newValue) => setFilters(prev => ({ ...prev, severity: newValue }))}
                    renderInput={(params) => (
                      <TextField {...params} label="Severity" placeholder="Select severities" />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          color={getSeverityColor(option) as any}
                          {...getTagProps({ index })}
                        />
                      ))
                    }
                  />
                </Grid>

                {/* Status Filter */}
                <Grid item xs={12} md={6}>
                  <Autocomplete
                    multiple
                    options={statusOptions}
                    value={filters.status}
                    onChange={(_, newValue) => setFilters(prev => ({ ...prev, status: newValue }))}
                    renderInput={(params) => (
                      <TextField {...params} label="Status" placeholder="Select statuses" />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          color={getStatusColor(option) as any}
                          {...getTagProps({ index })}
                        />
                      ))
                    }
                  />
                </Grid>

                {/* Category Filter */}
                <Grid item xs={12} md={6}>
                  <Autocomplete
                    multiple
                    options={categoryOptions}
                    value={filters.categories}
                    onChange={(_, newValue) => setFilters(prev => ({ ...prev, categories: newValue }))}
                    renderInput={(params) => (
                      <TextField {...params} label="Categories" placeholder="Select categories" />
                    )}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Results */}
        <Card>
          <CardContent>
            <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
              {tabLabels.map((label, index) => (
                <Tab key={index} label={label} />
              ))}
            </Tabs>

            {/* All Results Tab */}
            {activeTab === 0 && (
              <Box>
                {results.totalResults === 0 && !loading && (
                  <Box textAlign="center" py={4}>
                    <Typography variant="h6" color="textSecondary">
                      No results found
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Try adjusting your search query or filters
                    </Typography>
                  </Box>
                )}

                {/* Vulnerabilities Section */}
                {results.vulnerabilities.length > 0 && (
                  <Box mb={4}>
                    <Typography variant="h6" gutterBottom>
                      Vulnerabilities ({results.vulnerabilities.length})
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Service</TableCell>
                            <TableCell>Port</TableCell>
                            <TableCell>Severity</TableCell>
                            <TableCell>CVE ID</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {results.vulnerabilities.slice(0, 5).map((vuln) => (
                            <TableRow key={vuln.id}>
                              <TableCell>{vuln.service_name}</TableCell>
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
                                ) : 'N/A'}
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={vuln.status}
                                  color={getStatusColor(vuln.status) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <IconButton size="small">
                                  <Visibility />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                    {results.vulnerabilities.length > 5 && (
                      <Button
                        onClick={() => setActiveTab(1)}
                        sx={{ mt: 1 }}
                      >
                        View all {results.vulnerabilities.length} vulnerabilities
                      </Button>
                    )}
                  </Box>
                )}

                {/* Scans Section */}
                {results.scans.length > 0 && (
                  <Box mb={4}>
                    <Typography variant="h6" gutterBottom>
                      Scans ({results.scans.length})
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Filename</TableCell>
                            <TableCell>Target Hosts</TableCell>
                            <TableCell>Upload Date</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {results.scans.slice(0, 3).map((scan) => (
                            <TableRow key={scan.id}>
                              <TableCell>{scan.filename}</TableCell>
                              <TableCell>
                                {scan.target_hosts?.slice(0, 2).join(', ')}
                                {(scan.target_hosts?.length || 0) > 2 && ' ...'}
                              </TableCell>
                              <TableCell>
                                {new Date(scan.created_at).toLocaleDateString()}
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={scan.status}
                                  color={scan.status === 'completed' ? 'success' : 'warning'}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <IconButton size="small">
                                  <Visibility />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                    {results.scans.length > 3 && (
                      <Button
                        onClick={() => setActiveTab(2)}
                        sx={{ mt: 1 }}
                      >
                        View all {results.scans.length} scans
                      </Button>
                    )}
                  </Box>
                )}

                {/* Reports Section */}
                {results.reports.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Reports ({results.reports.length})
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Title</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Created</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {results.reports.slice(0, 3).map((report) => (
                            <TableRow key={report.id}>
                              <TableCell>{report.title}</TableCell>
                              <TableCell>{report.report_type}</TableCell>
                              <TableCell>
                                {new Date(report.created_at).toLocaleDateString()}
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={report.status}
                                  color={report.status === 'completed' ? 'success' : 'warning'}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <IconButton size="small">
                                  <Download />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                    {results.reports.length > 3 && (
                      <Button
                        onClick={() => setActiveTab(3)}
                        sx={{ mt: 1 }}
                      >
                        View all {results.reports.length} reports
                      </Button>
                    )}
                  </Box>
                )}
              </Box>
            )}

            {/* Individual tabs for each data type would go here */}
            {activeTab === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Vulnerability Results
                </Typography>
                {/* Full vulnerability table */}
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
                      {results.vulnerabilities.map((vuln) => (
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
                            ) : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {vuln.cvss_score ? vuln.cvss_score.toFixed(1) : 'N/A'}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={vuln.status}
                              color={getStatusColor(vuln.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton size="small">
                              <Visibility />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    );
};

export default Search;