import { severityHex } from './tokens';

// Map arbitrary severity strings to MUI Chip color prop
export const getSeverityColorName = (severity?: string): 'error' | 'warning' | 'info' | 'success' => {
  const s = (severity || '').toLowerCase();
  if (s === 'critical') return 'error';
  if (s === 'high') return 'warning';
  if (s === 'medium') return 'info';
  return 'success';
};

export const severityColorsHex = severityHex;

