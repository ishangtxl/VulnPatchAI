import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Paper,
  Chip,
  Alert,
  Snackbar,
  Tooltip,
} from '@mui/material';
import {
  ContentCopy,
  Warning,
  Security,
} from '@mui/icons-material';
import { RemediationCommand } from '../types';

interface CommandBlockProps {
  command: RemediationCommand;
  index: number;
}

const CommandBlock: React.FC<CommandBlockProps> = ({ command, index }) => {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(command.command);
      setCopySuccess(true);
    } catch (err) {
      console.error('Failed to copy command:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = command.command;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        setCopySuccess(true);
      } catch (fallbackErr) {
        console.error('Fallback copy failed:', fallbackErr);
      }
      document.body.removeChild(textArea);
    }
  };

  const handleSnackbarClose = () => {
    setCopySuccess(false);
  };

  const getOSColor = (os: string) => {
    switch (os.toLowerCase()) {
      case 'ubuntu':
      case 'debian':
        return '#E95420';
      case 'centos':
      case 'rhel':
        return '#262577';
      case 'macos':
        return '#000000';
      default:
        return '#1976d2';
    }
  };

  const getOSIcon = (os: string) => {
    switch (os.toLowerCase()) {
      case 'ubuntu':
        return '🐧';
      case 'debian':
        return '🌀';
      case 'centos':
      case 'rhel':
        return '🎩';
      case 'macos':
        return '🍎';
      default:
        return '💻';
    }
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Paper
        variant="outlined"
        sx={{
          p: 2,
          backgroundColor: '#f8f9fa',
          border: command.is_destructive ? '1px solid #ff9800' : '1px solid #e0e0e0',
          position: 'relative',
        }}
      >
        {/* Header with title and OS */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle2" fontWeight="bold" color="primary">
            {command.title}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={`${getOSIcon(command.os)} ${command.os.toUpperCase()}`}
              size="small"
              sx={{
                backgroundColor: getOSColor(command.os),
                color: 'white',
                fontWeight: 'bold',
              }}
            />
            {command.requires_sudo && (
              <Tooltip title="Requires administrator privileges">
                <Chip
                  icon={<Security />}
                  label="SUDO"
                  size="small"
                  color="warning"
                  variant="outlined"
                />
              </Tooltip>
            )}
            {command.is_destructive && (
              <Tooltip title="This command makes destructive changes">
                <Chip
                  icon={<Warning />}
                  label="DESTRUCTIVE"
                  size="small"
                  color="error"
                  variant="outlined"
                />
              </Tooltip>
            )}
          </Box>
        </Box>

        {/* Description */}
        {command.description && (
          <Typography variant="body2" color="textSecondary" sx={{ mb: 1.5 }}>
            {command.description}
          </Typography>
        )}

        {/* Command box */}
        <Box
          sx={{
            backgroundColor: '#1e1e1e',
            color: '#f8f8f2',
            padding: '12px 16px',
            borderRadius: '8px',
            fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
            fontSize: '14px',
            lineHeight: 1.4,
            position: 'relative',
            overflow: 'auto',
            border: command.is_destructive ? '2px solid #ff9800' : 'none',
          }}
        >
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {command.command}
          </pre>
          
          {/* Copy button */}
          <Tooltip title="Copy to clipboard">
            <IconButton
              onClick={handleCopyToClipboard}
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                color: '#f8f8f2',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                },
                width: 32,
                height: 32,
              }}
              size="small"
            >
              <ContentCopy fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Destructive warning */}
        {command.is_destructive && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            ⚠️ This command makes destructive changes. Please ensure you have backups before executing.
          </Alert>
        )}
      </Paper>

      {/* Success snackbar */}
      <Snackbar
        open={copySuccess}
        autoHideDuration={2000}
        onClose={handleSnackbarClose}
        message="Command copied to clipboard!"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
};

export default CommandBlock;