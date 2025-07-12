import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createTheme, ThemeProvider as MuiThemeProvider, Theme } from '@mui/material/styles';
import { PaletteMode } from '@mui/material';
import api from '../services/api';

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
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#ffffff',
      paper: '#f5f5f5',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1976d2',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#f5f5f5',
          borderRight: '1px solid #e0e0e0',
        },
      },
    },
  },
});

// Define dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b3b3b3',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1e1e1e',
          borderRight: '1px solid #333',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
        },
      },
    },
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