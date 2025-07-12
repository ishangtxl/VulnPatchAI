import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  Timeline,
  TrendingUp,
  TrendingDown,
  Warning,
  Security,
  Assessment,
  BugReport,
  Shield,
} from '@mui/icons-material';
import { dashboardAPI } from '../services/api';
import { DashboardMetrics, TrendData } from '../types';

// Mock data for predictive analytics (would come from backend)
const mockPredictiveData = {
  riskTrend: {
    current: 7.2,
    predicted: 5.8,
    change: -1.4,
    confidence: 0.85,
  },
  vulnerabilityForecast: [
    { month: 'Jan', predicted: 45, actual: 42 },
    { month: 'Feb', predicted: 38, actual: 41 },
    { month: 'Mar', predicted: 42, actual: 39 },
    { month: 'Apr', predicted: 35, actual: null },
    { month: 'May', predicted: 32, actual: null },
    { month: 'Jun', predicted: 29, actual: null },
  ],
  patchingEfficiency: {
    current: 78,
    target: 85,
    trend: 'improving',
    timeToTarget: '3 months',
  },
  topRisks: [
    { service: 'Apache HTTP Server', riskScore: 9.1, trend: 'increasing' },
    { service: 'OpenSSL', riskScore: 8.7, trend: 'stable' },
    { service: 'MySQL', riskScore: 7.9, trend: 'decreasing' },
    { service: 'PHP', riskScore: 7.3, trend: 'increasing' },
  ],
  complianceScore: {
    overall: 82,
    breakdown: {
      'SOC 2': 85,
      'PCI DSS': 78,
      'ISO 27001': 84,
      'NIST': 80,
    },
  },
};

const Analytics: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [trends, setTrends] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState('30');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [metricsData, trendsData] = await Promise.all([
          dashboardAPI.getMetrics(),
          dashboardAPI.getTrends(parseInt(timeRange)),
        ]);
        setMetrics(metricsData);
        setTrends(trendsData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load analytics data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

  const getRiskColor = (score: number) => {
    if (score >= 8) return 'error';
    if (score >= 6) return 'warning';
    if (score >= 4) return 'info';
    return 'success';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp color="error" />;
      case 'decreasing':
        return <TrendingDown color="success" />;
      default:
        return <Timeline color="action" />;
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
        <Typography variant="h4" gutterBottom>
          Predictive Analytics
        </Typography>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="7">Last 7 Days</MenuItem>
            <MenuItem value="30">Last 30 Days</MenuItem>
            <MenuItem value="90">Last 90 Days</MenuItem>
            <MenuItem value="365">Last Year</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Risk Prediction Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Risk Score Prediction</Typography>
              </Box>
              
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Box>
                  <Typography variant="h3" color="warning.main">
                    {mockPredictiveData.riskTrend.predicted}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Predicted (30 days)
                  </Typography>
                </Box>
                <Box textAlign="right">
                  <Typography variant="h4" color="textSecondary">
                    {mockPredictiveData.riskTrend.current}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Current
                  </Typography>
                </Box>
              </Box>

              <Box display="flex" alignItems="center" mb={2}>
                <TrendingDown color="success" sx={{ mr: 1 }} />
                <Typography variant="body2" color="success.main">
                  {Math.abs(mockPredictiveData.riskTrend.change)} point improvement expected
                </Typography>
              </Box>

              <Typography variant="caption" color="textSecondary">
                Confidence: {(mockPredictiveData.riskTrend.confidence * 100).toFixed(0)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Patching Efficiency */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Shield color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Patching Efficiency</Typography>
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Current Progress</Typography>
                  <Typography variant="body2">
                    {mockPredictiveData.patchingEfficiency.current}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={mockPredictiveData.patchingEfficiency.current}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Target</Typography>
                  <Typography variant="body2">
                    {mockPredictiveData.patchingEfficiency.target}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={mockPredictiveData.patchingEfficiency.target}
                  color="success"
                  sx={{ height: 4, borderRadius: 2 }}
                />
              </Box>

              <Typography variant="caption" color="textSecondary">
                Estimated time to target: {mockPredictiveData.patchingEfficiency.timeToTarget}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Vulnerability Forecast Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <BugReport color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Vulnerability Forecast</Typography>
              </Box>

              <Box sx={{ height: 200, display: 'flex', alignItems: 'end', gap: 2 }}>
                {mockPredictiveData.vulnerabilityForecast.map((item, index) => (
                  <Box key={item.month} sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'end', width: '100%', height: 150, gap: 1 }}>
                      {item.actual && (
                        <Box
                          sx={{
                            width: '45%',
                            height: `${(item.actual / 50) * 100}%`,
                            backgroundColor: 'primary.main',
                            borderRadius: 1,
                          }}
                        />
                      )}
                      <Box
                        sx={{
                          width: item.actual ? '45%' : '90%',
                          height: `${(item.predicted / 50) * 100}%`,
                          backgroundColor: item.actual ? 'warning.main' : 'info.main',
                          borderRadius: 1,
                          opacity: item.actual ? 0.8 : 1,
                          border: item.actual ? 'none' : '2px dashed',
                          borderColor: 'info.main',
                        }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ mt: 1 }}>
                      {item.month}
                    </Typography>
                  </Box>
                ))}
              </Box>

              <Box display="flex" justifyContent="center" gap={3} mt={2}>
                <Box display="flex" alignItems="center">
                  <Box sx={{ width: 16, height: 16, backgroundColor: 'primary.main', mr: 1 }} />
                  <Typography variant="caption">Actual</Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <Box sx={{ width: 16, height: 16, backgroundColor: 'warning.main', mr: 1 }} />
                  <Typography variant="caption">Predicted</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Risk Services */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Security color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">High-Risk Services</Typography>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Service</TableCell>
                      <TableCell>Risk Score</TableCell>
                      <TableCell>Trend</TableCell>
                      <TableCell>Action Required</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockPredictiveData.topRisks.map((risk, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {risk.service}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={risk.riskScore}
                            color={getRiskColor(risk.riskScore) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            {getTrendIcon(risk.trend)}
                            <Typography variant="caption" sx={{ ml: 1 }}>
                              {risk.trend}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={risk.riskScore >= 8 ? 'Immediate' : 'Scheduled'}
                            color={risk.riskScore >= 8 ? 'error' : 'warning'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Score */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Assessment color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Compliance Score</Typography>
              </Box>

              <Box textAlign="center" mb={3}>
                <Typography variant="h2" color="primary.main">
                  {mockPredictiveData.complianceScore.overall}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Overall Score
                </Typography>
              </Box>

              <Divider sx={{ mb: 2 }} />

              {Object.entries(mockPredictiveData.complianceScore.breakdown).map(([framework, score]) => (
                <Box key={framework} mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">{framework}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {score}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={score}
                    color={score >= 80 ? 'success' : score >= 70 ? 'warning' : 'error'}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Current Metrics Summary */}
        {metrics && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Security Metrics
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary.main">
                        {metrics.total_scans}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Total Scans
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="error.main">
                        {metrics.vulnerabilities.critical}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Critical Vulnerabilities
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        {metrics.patch_completion_rate}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Patch Completion
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="warning.main">
                        {metrics.avg_cvss_score.toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Avg CVSS Score
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Analytics;