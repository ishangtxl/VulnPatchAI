import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  CloudUpload,
  CheckCircle,
  Error,
  Schedule,
  ContentCopy,
  Info,
  ExpandMore,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { scanAPI } from '../services/api';
import { Scan } from '../types';

const ScanUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadedScans, setUploadedScans] = useState<Scan[]>([]);
  const [error, setError] = useState<string>('');

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    setError('');
    
    for (const file of acceptedFiles) {
      if (!file.name.endsWith('.xml')) {
        setError('Only XML files are allowed');
        continue;
      }

      if (file.size > 10 * 1024 * 1024) { // 10MB
        setError('File size must be less than 10MB');
        continue;
      }

      setUploading(true);
      try {
        const scan = await scanAPI.upload(file);
        setUploadedScans(prev => [scan, ...prev]);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Upload failed');
      } finally {
        setUploading(false);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
    },
    multiple: true,
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
        return <Error color="error" />;
      case 'processing':
        return <Schedule color="warning" />;
      default:
        return <Schedule />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Nmap Scan
      </Typography>

      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? 'Drop the XML files here...'
            : 'Drag & drop Nmap XML files here, or click to select'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Supports multiple files up to 10MB each
        </Typography>
        <Button
          variant="contained"
          sx={{ mt: 2 }}
          disabled={uploading}
        >
          Select Files
        </Button>
      </Paper>

      {uploading && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" gutterBottom>
            Uploading and processing...
          </Typography>
          <LinearProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {uploadedScans.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Uploads
          </Typography>
          <List>
            {uploadedScans.map((scan) => (
              <ListItem key={scan.id} divider>
                <ListItemIcon>
                  {getStatusIcon(scan.status)}
                </ListItemIcon>
                <ListItemText
                  primary={scan.filename}
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Uploaded: {new Date(scan.upload_time).toLocaleString()}
                      </Typography>
                      {scan.file_size && (
                        <Typography variant="body2" color="textSecondary">
                          Size: {(scan.file_size / 1024).toFixed(1)} KB
                        </Typography>
                      )}
                      {scan.error_message && (
                        <Typography variant="body2" color="error">
                          Error: {scan.error_message}
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Chip
                  label={scan.status}
                  color={getStatusColor(scan.status) as any}
                  size="small"
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Box sx={{ mt: 3 }}>
        <Alert severity="info">
          <Typography variant="h6" gutterBottom>
            Upload Instructions
          </Typography>
          <Typography variant="body2" component="div">
            <ul>
              <li>Upload Nmap XML scan results for vulnerability analysis</li>
              <li>Files will be automatically parsed and analyzed using AI</li>
              <li>Processing typically takes 30-60 seconds per file</li>
              <li>You can view results in the Dashboard and Vulnerabilities sections</li>
            </ul>
          </Typography>
        </Alert>
      </Box>

      {/* Nmap Information Box */}
      <Box sx={{ mt: 3 }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" alignItems="center" gap={1}>
              <Info color="primary" />
              <Typography variant="h6">What is Nmap & How to Generate XML Scans</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="body2" gutterBottom sx={{ mb: 2 }}>
                <strong>Nmap</strong> is a powerful network scanning tool used to discover hosts, services, and security vulnerabilities on computer networks.
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2, mb: 1 }}>
                Generate Nmap XML files with these commands:
              </Typography>
              
              {/* Ubuntu/Linux Commands */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  Ubuntu/Linux:
                </Typography>
                <Box sx={{ 
                  bgcolor: '#f5f5f5', 
                  p: 2, 
                  borderRadius: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  fontFamily: 'monospace'
                }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    sudo nmap -sV -sC -oX scan_results.xml &lt;target_ip&gt;
                  </Typography>
                  <Tooltip title="Copy command">
                    <IconButton 
                      size="small" 
                      onClick={() => copyToClipboard('sudo nmap -sV -sC -oX scan_results.xml <target_ip>')}
                    >
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>

              {/* macOS Commands */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  macOS:
                </Typography>
                <Box sx={{ 
                  bgcolor: '#f5f5f5', 
                  p: 2, 
                  borderRadius: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  fontFamily: 'monospace'
                }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    brew install nmap && nmap -sV -sC -oX scan_results.xml &lt;target_ip&gt;
                  </Typography>
                  <Tooltip title="Copy command">
                    <IconButton 
                      size="small" 
                      onClick={() => copyToClipboard('brew install nmap && nmap -sV -sC -oX scan_results.xml <target_ip>')}
                    >
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>

              <Typography variant="caption" color="textSecondary">
                Replace &lt;target_ip&gt; with the actual IP address or hostname you want to scan. 
                The -sV flag detects service versions, -sC runs default scripts, and -oX outputs results in XML format.
              </Typography>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Box>
  );
};

export default ScanUpload;