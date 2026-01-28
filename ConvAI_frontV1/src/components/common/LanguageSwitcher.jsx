import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Tooltip,
  Box
} from '@mui/material';
import { Language, Check } from '@mui/icons-material';

const languages = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳' }
];

const LanguageSwitcher = ({ variant = 'icon' }) => {
  const { i18n, t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (langCode) => {
    i18n.changeLanguage(langCode);
    handleClose();
  };

  const currentLang = languages.find(l => l.code === i18n.language) || languages[0];

  if (variant === 'button') {
    return (
      <Box sx={{ display: 'flex', gap: 1 }}>
        {languages.map((lang) => (
          <Box
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            sx={{
              px: 2,
              py: 1,
              borderRadius: 2,
              cursor: 'pointer',
              border: '2px solid',
              borderColor: i18n.language === lang.code ? 'primary.main' : 'divider',
              backgroundColor: i18n.language === lang.code ? 'primary.light' : 'background.paper',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'primary.light',
              }
            }}
          >
            <Typography variant="body2" fontWeight={i18n.language === lang.code ? 700 : 400}>
              {lang.flag} {lang.nativeName}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  }

  return (
    <>
      <Tooltip title={t('settings.selectLanguage')}>
        <IconButton
          onClick={handleClick}
          sx={{
            color: 'inherit',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            }
          }}
        >
          <Language />
          <Typography variant="caption" sx={{ ml: 0.5, fontWeight: 600 }}>
            {currentLang.code.toUpperCase()}
          </Typography>
        </IconButton>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 180,
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
            borderRadius: 2,
          }
        }}
      >
        <Typography 
          variant="caption" 
          sx={{ 
            px: 2, 
            py: 1, 
            display: 'block', 
            color: 'text.secondary',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: 1
          }}
        >
          {t('settings.selectLanguage')}
        </Typography>
        
        {languages.map((lang) => (
          <MenuItem
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            selected={i18n.language === lang.code}
            sx={{
              py: 1.5,
              '&.Mui-selected': {
                backgroundColor: 'primary.light',
              }
            }}
          >
            <ListItemIcon sx={{ fontSize: 20, minWidth: 36 }}>
              {lang.flag}
            </ListItemIcon>
            <ListItemText>
              <Typography variant="body2" fontWeight={500}>
                {lang.nativeName}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {lang.name}
              </Typography>
            </ListItemText>
            {i18n.language === lang.code && (
              <Check sx={{ color: 'primary.main', ml: 1 }} />
            )}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default LanguageSwitcher;
