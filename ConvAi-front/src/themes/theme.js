import { createTheme } from '@mui/material/styles';

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4f46e5', // Modern indigo
      light: '#818cf8',
      dark: '#3730a3',
      contrastText: '#ffffff',
      50: '#f8faff',
      100: '#e0e7ff',
      200: '#c7d2fe',
      300: '#a5b4fc',
      400: '#818cf8',
      500: '#6366f1',
      600: '#4f46e5',
      700: '#4338ca',
      800: '#3730a3',
      900: '#312e81',
    },
    secondary: {
      main: '#06b6d4', // Cyan accent
      light: '#67e8f9',
      dark: '#0891b2',
      contrastText: '#ffffff',
      50: '#ecfeff',
      100: '#cffafe',
      200: '#a5f3fc',
      300: '#67e8f9',
      400: '#22d3ee',
      500: '#06b6d4',
      600: '#0891b2',
      700: '#0e7490',
      800: '#155e75',
      900: '#164e63',
    },
    accent: {
      main: '#8b5cf6', // Purple accent
      light: '#c4b5fd',
      dark: '#7c3aed',
      contrastText: '#ffffff',
    },
    success: {
      main: '#10b981',
      light: '#6ee7b7',
      dark: '#047857',
      contrastText: '#ffffff',
    },
    error: {
      main: '#ef4444',
      light: '#fca5a5',
      dark: '#dc2626',
      contrastText: '#ffffff',
    },
    warning: {
      main: '#f59e0b',
      light: '#fcd34d',
      dark: '#d97706',
      contrastText: '#ffffff',
    },
    info: {
      main: '#3b82f6',
      light: '#93c5fd',
      dark: '#1d4ed8',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      aiGradient: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 50%, #8b5cf6 100%)',
      cardGradient: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
      tertiary: '#94a3b8',
      gradient: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
    },
    divider: 'rgba(148, 163, 184, 0.12)',
    glass: {
      background: 'rgba(255, 255, 255, 0.1)',
      border: 'rgba(255, 255, 255, 0.2)',
      shadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
    },
  },
  typography: {
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
    h1: {
      fontSize: 'clamp(2rem, 5vw, 3.5rem)',
      fontWeight: 800,
      lineHeight: 1.1,
      background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
      letterSpacing: '-0.02em',
      '@media (max-width: 640px)': {
        fontSize: '2rem',
        lineHeight: 1.2,
      },
    },
    h2: {
      fontSize: 'clamp(1.75rem, 4vw, 2.75rem)',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.01em',
      '@media (max-width: 640px)': {
        fontSize: '1.75rem',
        lineHeight: 1.3,
      },
    },
    h3: {
      fontSize: 'clamp(1.5rem, 3vw, 2.25rem)',
      fontWeight: 700,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
      '@media (max-width: 640px)': {
        fontSize: '1.5rem',
        lineHeight: 1.4,
      },
    },
    h4: {
      fontSize: 'clamp(1.25rem, 2.5vw, 1.875rem)',
      fontWeight: 600,
      lineHeight: 1.3,
      '@media (max-width: 640px)': {
        fontSize: '1.25rem',
        lineHeight: 1.4,
      },
    },
    h5: {
      fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
      fontWeight: 600,
      lineHeight: 1.4,
      '@media (max-width: 640px)': {
        fontSize: '1.125rem',
        lineHeight: 1.5,
      },
    },
    h6: {
      fontSize: 'clamp(1rem, 1.5vw, 1.25rem)',
      fontWeight: 600,
      lineHeight: 1.4,
      '@media (max-width: 640px)': {
        fontSize: '1rem',
        lineHeight: 1.5,
      },
    },
    subtitle1: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.5,
      color: '#64748b',
    },
    subtitle2: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.5,
      color: '#64748b',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.7,
      fontWeight: 400,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
      fontWeight: 400,
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
      fontWeight: 400,
      color: '#94a3b8',
    },
    overline: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
      color: '#64748b',
    },
  },
  shape: {
    borderRadius: 16,
  },
  spacing: 8,
  breakpoints: {
    values: {
      xs: 0,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      xxl: 1536,
    },
  },
  shadows: [
    'none',
    '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)',
    '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)',
    '0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)',
    '0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)',
    '0px 3px 5px -1px rgba(0,0,0,0.2),0px 5px 8px 0px rgba(0,0,0,0.14),0px 1px 14px 0px rgba(0,0,0,0.12)',
    '0px 3px 5px -1px rgba(0,0,0,0.2),0px 6px 10px 0px rgba(0,0,0,0.14),0px 1px 18px 0px rgba(0,0,0,0.12)',
    '0px 4px 5px -2px rgba(0,0,0,0.2),0px 7px 10px 1px rgba(0,0,0,0.14),0px 2px 16px 1px rgba(0,0,0,0.12)',
    '0px 5px 5px -3px rgba(0,0,0,0.2),0px 8px 10px 1px rgba(0,0,0,0.14),0px 3px 14px 2px rgba(0,0,0,0.12)',
    '0px 5px 6px -3px rgba(0,0,0,0.2),0px 9px 12px 1px rgba(0,0,0,0.14),0px 3px 16px 2px rgba(0,0,0,0.12)',
    '0px 6px 6px -3px rgba(0,0,0,0.2),0px 10px 14px 1px rgba(0,0,0,0.14),0px 4px 18px 3px rgba(0,0,0,0.12)',
    '0px 6px 7px -4px rgba(0,0,0,0.2),0px 11px 15px 1px rgba(0,0,0,0.14),0px 4px 20px 3px rgba(0,0,0,0.12)',
    '0px 7px 8px -4px rgba(0,0,0,0.2),0px 12px 17px 2px rgba(0,0,0,0.14),0px 5px 22px 4px rgba(0,0,0,0.12)',
    '0px 7px 8px -4px rgba(0,0,0,0.2),0px 13px 19px 2px rgba(0,0,0,0.14),0px 5px 24px 4px rgba(0,0,0,0.12)',
    '0px 7px 9px -4px rgba(0,0,0,0.2),0px 14px 21px 2px rgba(0,0,0,0.14),0px 5px 26px 4px rgba(0,0,0,0.12)',
    '0px 8px 9px -5px rgba(0,0,0,0.2),0px 15px 22px 2px rgba(0,0,0,0.14),0px 6px 28px 5px rgba(0,0,0,0.12)',
    '0px 8px 10px -5px rgba(0,0,0,0.2),0px 16px 24px 2px rgba(0,0,0,0.14),0px 6px 30px 5px rgba(0,0,0,0.12)',
    '0px 8px 11px -5px rgba(0,0,0,0.2),0px 17px 26px 2px rgba(0,0,0,0.14),0px 6px 32px 5px rgba(0,0,0,0.12)',
    '0px 9px 11px -5px rgba(0,0,0,0.2),0px 18px 28px 2px rgba(0,0,0,0.14),0px 7px 34px 6px rgba(0,0,0,0.12)',
    '0px 9px 12px -6px rgba(0,0,0,0.2),0px 19px 29px 2px rgba(0,0,0,0.14),0px 7px 36px 6px rgba(0,0,0,0.12)',
    '0px 10px 13px -6px rgba(0,0,0,0.2),0px 20px 31px 3px rgba(0,0,0,0.14),0px 8px 38px 7px rgba(0,0,0,0.12)',
    '0px 10px 13px -6px rgba(0,0,0,0.2),0px 21px 33px 3px rgba(0,0,0,0.14),0px 8px 40px 7px rgba(0,0,0,0.12)',
    '0px 10px 14px -6px rgba(0,0,0,0.2),0px 22px 35px 3px rgba(0,0,0,0.14),0px 8px 42px 7px rgba(0,0,0,0.12)',
    '0px 11px 14px -7px rgba(0,0,0,0.2),0px 23px 36px 3px rgba(0,0,0,0.14),0px 9px 44px 8px rgba(0,0,0,0.12)',
    '0px 11px 15px -7px rgba(0,0,0,0.2),0px 24px 38px 3px rgba(0,0,0,0.14),0px 9px 46px 8px rgba(0,0,0,0.12)',
  ],
  components: {
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: '16px',
          paddingRight: '16px',
          '@media (min-width: 640px)': {
            paddingLeft: '24px',
            paddingRight: '24px',
          },
          '@media (min-width: 768px)': {
            paddingLeft: '32px',
            paddingRight: '32px',
          },
          '@media (min-width: 1024px)': {
            paddingLeft: '40px',
            paddingRight: '40px',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 12,
          padding: '8px 16px',
          fontSize: '0.875rem',
          boxShadow: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '@media (min-width: 640px)': {
            padding: '10px 20px',
            fontSize: '0.95rem',
            borderRadius: 14,
          },
          '@media (min-width: 768px)': {
            padding: '12px 24px',
            fontSize: '1rem',
            borderRadius: 16,
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
            transition: 'left 0.5s',
          },
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(79, 70, 229, 0.3)',
          },
          '&:hover::before': {
            left: '100%',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
          color: '#ffffff',
          '&:hover': {
            background: 'linear-gradient(135deg, #4338ca 0%, #6d28d9 100%)',
            boxShadow: '0 12px 30px rgba(79, 70, 229, 0.4)',
          },
        },
        outlined: {
          border: '2px solid rgba(79, 70, 229, 0.2)',
          color: '#4f46e5',
          '&:hover': {
            border: '2px solid rgba(79, 70, 229, 0.4)',
            background: 'rgba(79, 70, 229, 0.05)',
          },
        },
        text: {
          '&:hover': {
            background: 'rgba(79, 70, 229, 0.08)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: 12,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '@media (min-width: 640px)': {
            borderRadius: 16,
          },
          '@media (min-width: 768px)': {
            borderRadius: 20,
          },
          '@media (min-width: 1024px)': {
            borderRadius: 24,
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
            transition: 'left 0.5s',
            zIndex: 1,
            pointerEvents: 'none',
          },
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(79, 70, 229, 0.1)',
            '@media (min-width: 768px)': {
              transform: 'translateY(-6px)',
            },
          },
          '&:hover::before': {
            left: '100%',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '@media (min-width: 768px)': {
              borderRadius: 16,
            },
            '& fieldset': {
              border: '1px solid rgba(79, 70, 229, 0.1)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            },
            '&:hover fieldset': {
              border: '1px solid rgba(79, 70, 229, 0.3)',
            },
            '&.Mui-focused fieldset': {
              border: '2px solid #4f46e5',
            },
            '&.Mui-focused': {
              boxShadow: '0 0 0 4px rgba(79, 70, 229, 0.1)',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: 20,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
        elevation1: {
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
        },
        elevation2: {
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)',
        },
        elevation3: {
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontWeight: 500,
          background: 'rgba(79, 70, 229, 0.1)',
          border: '1px solid rgba(79, 70, 229, 0.2)',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            background: 'rgba(79, 70, 229, 0.15)',
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(79, 70, 229, 0.2)',
          },
        },
        clickable: {
          '&:active': {
            transform: 'translateY(0)',
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'scale(1.1)',
            background: 'rgba(79, 70, 229, 0.1)',
          },
          '&:active': {
            transform: 'scale(0.95)',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          borderRadius: 16,
          padding: '4px',
          minHeight: 48,
        },
        indicator: {
          display: 'none',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 500,
          minHeight: 40,
          color: '#64748b',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&.Mui-selected': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
            color: '#ffffff',
            fontWeight: 600,
            boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)',
          },
          '&:hover': {
            background: 'rgba(79, 70, 229, 0.1)',
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 8,
          background: 'rgba(79, 70, 229, 0.1)',
        },
        bar: {
          borderRadius: 8,
          background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
          boxShadow: '0 0 10px rgba(79, 70, 229, 0.3)',
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
          fontWeight: 600,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'scale(1.05)',
            boxShadow: '0 8px 20px rgba(79, 70, 229, 0.3)',
          },
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          background: 'rgba(15, 23, 42, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: 8,
          padding: '8px 12px',
          fontSize: '0.75rem',
          fontWeight: 500,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        },
        arrow: {
          color: 'rgba(15, 23, 42, 0.95)',
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        root: {
          width: 48,
          height: 28,
          padding: 0,
        },
        switchBase: {
          padding: 2,
          '&.Mui-checked': {
            transform: 'translateX(20px)',
            '& + .MuiSwitch-track': {
              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              opacity: 1,
            },
          },
        },
        thumb: {
          width: 24,
          height: 24,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
        },
        track: {
          borderRadius: 14,
          background: 'rgba(148, 163, 184, 0.3)',
          opacity: 1,
        },
      },
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
      contrastText: '#ffffff',
      50: '#1e1b4b',
      100: '#312e81',
      200: '#3730a3',
      300: '#4338ca',
      400: '#4f46e5',
      500: '#6366f1',
      600: '#818cf8',
      700: '#a5b4fc',
      800: '#c7d2fe',
      900: '#e0e7ff',
    },
    secondary: {
      main: '#22d3ee',
      light: '#67e8f9',
      dark: '#0891b2',
      contrastText: '#ffffff',
      50: '#083344',
      100: '#164e63',
      200: '#155e75',
      300: '#0e7490',
      400: '#0891b2',
      500: '#06b6d4',
      600: '#22d3ee',
      700: '#67e8f9',
      800: '#a5f3fc',
      900: '#cffafe',
    },
    accent: {
      main: '#a855f7',
      light: '#c4b5fd',
      dark: '#7c3aed',
      contrastText: '#ffffff',
    },
    success: {
      main: '#34d399',
      light: '#6ee7b7',
      dark: '#10b981',
      contrastText: '#ffffff',
    },
    error: {
      main: '#f87171',
      light: '#fca5a5',
      dark: '#ef4444',
      contrastText: '#ffffff',
    },
    warning: {
      main: '#fbbf24',
      light: '#fcd34d',
      dark: '#f59e0b',
      contrastText: '#ffffff',
    },
    info: {
      main: '#60a5fa',
      light: '#93c5fd',
      dark: '#3b82f6',
      contrastText: '#ffffff',
    },
    background: {
      default: '#0a0f23',
      paper: 'rgba(15, 23, 42, 0.8)',
      gradient: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      aiGradient: 'linear-gradient(135deg, #312e81 0%, #1e40af 50%, #6d28d9 100%)',
      cardGradient: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.7) 100%)',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#cbd5e1',
      tertiary: '#94a3b8',
      gradient: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
    },
    divider: 'rgba(148, 163, 184, 0.2)',
    glass: {
      background: 'rgba(30, 41, 59, 0.3)',
      border: 'rgba(148, 163, 184, 0.1)',
      shadow: '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
    },
  },
  typography: {
    ...lightTheme.typography,
    h1: {
      ...lightTheme.typography.h1,
      background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
    },
  },
  shape: lightTheme.shape,
  spacing: lightTheme.spacing,
  breakpoints: lightTheme.breakpoints,
  components: {
    ...lightTheme.components,
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(30, 41, 59, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          borderRadius: 24,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.2), transparent)',
            transition: 'left 0.5s',
            zIndex: 1,
            pointerEvents: 'none',
          },
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(99, 102, 241, 0.3)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
          },
          '&:hover::before': {
            left: '100%',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          ...lightTheme.components.MuiButton.styleOverrides.root,
        },
        contained: {
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #9333ea 100%)',
            boxShadow: '0 12px 30px rgba(99, 102, 241, 0.4)',
          },
        },
        outlined: {
          border: '2px solid rgba(99, 102, 241, 0.3)',
          color: '#818cf8',
          '&:hover': {
            border: '2px solid rgba(99, 102, 241, 0.5)',
            background: 'rgba(99, 102, 241, 0.1)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            background: 'rgba(30, 41, 59, 0.6)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '& fieldset': {
              border: '1px solid rgba(99, 102, 241, 0.2)',
            },
            '&:hover fieldset': {
              border: '1px solid rgba(99, 102, 241, 0.4)',
            },
            '&.Mui-focused fieldset': {
              border: '2px solid #6366f1',
            },
            '&.Mui-focused': {
              boxShadow: '0 0 0 4px rgba(99, 102, 241, 0.2)',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          background: 'rgba(30, 41, 59, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          background: 'rgba(30, 41, 59, 0.6)',
          backdropFilter: 'blur(10px)',
          borderRadius: 16,
          padding: '4px',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          ...lightTheme.components.MuiTab.styleOverrides.root,
          color: '#cbd5e1',
          '&.Mui-selected': {
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            color: '#ffffff',
            fontWeight: 600,
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
          },
          '&:hover': {
            background: 'rgba(99, 102, 241, 0.15)',
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          background: 'rgba(99, 102, 241, 0.15)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            background: 'rgba(99, 102, 241, 0.25)',
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 8,
          background: 'rgba(99, 102, 241, 0.15)',
        },
        bar: {
          borderRadius: 8,
          background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
          boxShadow: '0 0 10px rgba(99, 102, 241, 0.4)',
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          fontWeight: 600,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'scale(1.05)',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)',
          },
        },
      },
    },
  },
});

export { lightTheme, darkTheme };