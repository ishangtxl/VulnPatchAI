// Centralized design tokens for VulnPatch AI UI
export const palette = {
  light: {
    mode: 'light' as const,
    primary: { main: '#1E88E5' },
    secondary: { main: '#7E57C2' },
    info: { main: '#0288D1' },
    success: { main: '#2E7D32' },
    warning: { main: '#ED6C02' },
    error: { main: '#D32F2F' },
    background: { default: '#FAFBFC', paper: '#FFFFFF' },
    text: { primary: '#212121', secondary: '#616161' },
    divider: '#E0E0E0',
  },
  dark: {
    mode: 'dark' as const,
    primary: { main: '#90CAF9' },
    secondary: { main: '#B39DDB' },
    info: { main: '#81D4FA' },
    success: { main: '#81C784' },
    warning: { main: '#FFB74D' },
    error: { main: '#EF9A9A' },
    background: { default: '#121212', paper: '#1E1E1E' },
    text: { primary: '#FFFFFF', secondary: '#BDBDBD' },
    divider: '#2C2C2C',
  },
};

export const severityHex = {
  critical: '#B71C1C',
  high: '#E65100',
  medium: '#F9A825',
  low: '#2E7D32',
};

export const spacing = (factor: number) => `${factor * 4}px`;
export const radii = { sm: 6, md: 8, lg: 12, pill: 999 };
export const shadows = {
  card: '0 1px 2px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)',
};

export const chartSeries = {
  severity: [severityHex.critical, severityHex.high, severityHex.medium, severityHex.low],
};

