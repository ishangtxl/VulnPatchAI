import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createTheme, ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { PaletteMode } from '@mui/material';
import api from '../services/api';
import { palette, radii, shadows } from '../styles/tokens';

interface ThemeContextType {
  mode: PaletteMode;
  toggleTheme: () => void;
  setTheme: (mode: PaletteMode) => void;
  loadUserPreferences: () => Promise<void>;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

// Define light theme
const lightTheme = createTheme({
  palette: palette.light as any,
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: 32, lineHeight: 1.25, fontWeight: 600 },
    h2: { fontSize: 24, lineHeight: 1.33, fontWeight: 600 },
    h3: { fontSize: 20, lineHeight: 1.4, fontWeight: 600 },
    body1: { fontSize: 16, lineHeight: 1.5 },
    body2: { fontSize: 14, lineHeight: 1.45 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: palette.light.background.default },
        '*:focus-visible': { outline: '2px solid #5B9DFF', outlineOffset: 2 },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderBottom: `1px solid ${palette.light.divider}`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: palette.light.background.paper,
          borderRight: `1px solid ${palette.light.divider}`,
        },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          borderRadius: radii.lg,
          boxShadow: shadows.card,
          border: `1px solid ${palette.light.divider}`,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: radii.md,
        },
      },
    },
    MuiButton: {
      defaultProps: { size: 'small', disableElevation: true },
      styleOverrides: {
        root: { borderRadius: radii.md },
      },
    },
    MuiTextField: {
      defaultProps: { size: 'small' },
    },
    MuiChip: {
      defaultProps: { size: 'small' },
    },
    MuiTableCell: {
      styleOverrides: { root: { paddingTop: 8, paddingBottom: 8 } },
    },
  },
});

// Define dark theme
const darkTheme = createTheme({
  palette: palette.dark as any,
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: 32, lineHeight: 1.25, fontWeight: 600 },
    h2: { fontSize: 24, lineHeight: 1.33, fontWeight: 600 },
    h3: { fontSize: 20, lineHeight: 1.4, fontWeight: 600 },
    body1: { fontSize: 16, lineHeight: 1.5 },
    body2: { fontSize: 14, lineHeight: 1.45 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: palette.dark.background.default },
        '*:focus-visible': { outline: '2px solid #5B9DFF', outlineOffset: 2 },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderBottom: `1px solid ${palette.dark.divider}`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: palette.dark.background.paper,
          borderRight: `1px solid ${palette.dark.divider}`,
        },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          borderRadius: radii.lg,
          boxShadow: shadows.card,
          border: `1px solid ${palette.dark.divider}`,
        },
      },
    },
    MuiPaper: {
      styleOverrides: { root: { borderRadius: radii.md } },
    },
    MuiButton: {
      defaultProps: { size: 'small', disableElevation: true },
      styleOverrides: { root: { borderRadius: radii.md } },
    },
    MuiTextField: { defaultProps: { size: 'small' } },
    MuiChip: { defaultProps: { size: 'small' } },
    MuiTableCell: { styleOverrides: { root: { paddingTop: 8, paddingBottom: 8 } } },
  },
});

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<PaletteMode>(() => {
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('vulnpatch-theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      return savedTheme as PaletteMode;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  });

  const [preferencesLoaded, setPreferencesLoaded] = useState(false);

  const toggleTheme = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setTheme(newMode);
  };

  const setTheme = async (newMode: PaletteMode) => {
    setMode(newMode);
    localStorage.setItem('vulnpatch-theme', newMode);
    
    // Temporarily disable backend sync to prevent unauthorized requests
    // TODO: Re-enable after proper authentication flow
    console.log('Theme preference saved locally only - backend sync disabled');
    
    /* // Update user preference on backend only if user is authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await api.patch('/theme/preferences', {
          theme_preference: newMode
        });
      } catch (error) {
        console.warn('Failed to save theme preference to backend:', error);
      }
    } */
  };

  // Listen for system theme changes when in auto mode
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      const savedTheme = localStorage.getItem('vulnpatch-theme');
      if (savedTheme === 'auto' || !savedTheme) {
        setMode(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const loadUserPreferences = async () => {
    const token = localStorage.getItem('access_token');
    if (!token || preferencesLoaded) {
      return; // Skip API call if not authenticated or already loaded
    }

    // Temporarily disable API calls to prevent unauthorized requests
    // TODO: Re-enable after user authentication flow is properly handled
    console.log('Theme preferences API call skipped - authentication required');
    setPreferencesLoaded(true);
    
    /* try {
      const response = await api.get('/theme/preferences');
      if (response.data.theme_preference) {
        setMode(response.data.theme_preference);
        localStorage.setItem('vulnpatch-theme', response.data.theme_preference);
      }
      setPreferencesLoaded(true);
    } catch (error) {
      console.warn('Failed to load theme preference from backend:', error);
      setPreferencesLoaded(true); // Mark as loaded even on error to prevent retries
    } */
  };

  // Load user preference from backend on mount only if authenticated
  useEffect(() => {
    // Don't make API calls on initial load - only load from localStorage
    // User preferences will be loaded after login via loadUserPreferences()
  }, []);

  const theme = mode === 'light' ? lightTheme : darkTheme;

  const value = {
    mode,
    toggleTheme,
    setTheme,
    loadUserPreferences,
  };

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
