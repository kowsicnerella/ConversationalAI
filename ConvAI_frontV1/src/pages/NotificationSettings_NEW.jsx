import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  FormGroup,
  FormControlLabel,
  Switch,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Chip,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Save as SaveIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import API from '../config/api';

const NotificationSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [settings, setSettings] = useState({
    daily_reminder_enabled: true,
    daily_reminder_time: '19:00',
    weekend_reminders: true,
    quiet_hours_enabled: false,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    timezone: 'Asia/Kolkata',
    notification_types: {},
    delivery_channels: {
      in_app: true,
      email: false,
      push: false,
    },
  });

  const [notificationTypes, setNotificationTypes] = useState([]);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await API.get('/notifications/preferences');
      if (response.data.success) {
        const prefs = response.data.preferences;
        
        setSettings({
          daily_reminder_enabled: prefs.daily_reminder_enabled ?? true,
          daily_reminder_time: prefs.daily_reminder_time || '19:00',
          weekend_reminders: prefs.weekend_reminders ?? true,
          quiet_hours_enabled: prefs.quiet_hours_start && prefs.quiet_hours_end,
          quiet_hours_start: prefs.quiet_hours_start || '22:00',
          quiet_hours_end: prefs.quiet_hours_end || '08:00',
          timezone: prefs.timezone || 'Asia/Kolkata',
          notification_types: prefs.notification_types || {},
          delivery_channels: prefs.delivery_channels || {
            in_app: true,
            email: false,
            push: false,
          },
        });

        if (prefs.notification_types) {
          const types = Object.keys(prefs.notification_types).map(key => ({
            name: key,
            display_name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            enabled: prefs.notification_types[key],
          }));
          setNotificationTypes(types);
        }
      }
    } catch (err) {
      setError('Failed to load settings. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      await API.put('/notifications/preferences', {
        daily_reminder_enabled: settings.daily_reminder_enabled,
        daily_reminder_time: settings.daily_reminder_time,
        weekend_reminders: settings.weekend_reminders,
        quiet_hours_start: settings.quiet_hours_enabled ? settings.quiet_hours_start : null,
        quiet_hours_end: settings.quiet_hours_enabled ? settings.quiet_hours_end : null,
        timezone: settings.timezone,
        notification_types: settings.notification_types,
        delivery_channels: settings.delivery_channels,
      });

      setSuccess('Settings saved successfully!');
    } catch (err) {
      setError('Failed to save settings. Please try again.');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleNotificationType = (typeName) => {
    setSettings(prev => ({
      ...prev,
      notification_types: {
        ...prev.notification_types,
        [typeName]: !prev.notification_types[typeName],
      },
    }));
  };

  const handleToggleDeliveryChannel = (channel) => {
    setSettings(prev => ({
      ...prev,
      delivery_channels: {
        ...prev.delivery_channels,
        [channel]: !prev.delivery_channels[channel],
      },
    }));
  };

  const timezones = [
    'Asia/Kolkata',
    'America/New_York',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Australia/Sydney',
  ];

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Notification Settings
        </Typography>
        <Typography color="text.secondary">
          Customize how and when you receive notifications
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotificationsIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Notification Types</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Choose which types of notifications you want to receive
          </Typography>

          <FormGroup>
            {notificationTypes.map((type) => (
              <FormControlLabel
                key={type.name}
                control={
                  <Switch
                    checked={settings.notification_types[type.name] ?? true}
                    onChange={() => handleToggleNotificationType(type.name)}
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography>{type.display_name}</Typography>
                    {settings.notification_types[type.name] && (
                      <Chip label="Enabled" size="small" color="success" />
                    )}
                  </Box>
                }
              />
            ))}
          </FormGroup>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Daily Reminder
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get a daily reminder to practice your English
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.daily_reminder_enabled}
                onChange={(e) => setSettings(prev => ({ ...prev, daily_reminder_enabled: e.target.checked }))}
              />
            }
            label="Enable Daily Reminder"
            sx={{ mb: 2 }}
          />

          {settings.daily_reminder_enabled && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Reminder Time"
                  type="time"
                  value={settings.daily_reminder_time}
                  onChange={(e) => {
                    setSettings(prev => ({ ...prev, daily_reminder_time: e.target.value }));
                  }}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Timezone</InputLabel>
                  <Select
                    value={settings.timezone}
                    label="Timezone"
                    onChange={(e) => setSettings(prev => ({ ...prev, timezone: e.target.value }))}
                  >
                    {timezones.map((tz) => (
                      <MenuItem key={tz} value={tz}>{tz}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.weekend_reminders}
                      onChange={(e) => setSettings(prev => ({ ...prev, weekend_reminders: e.target.checked }))}
                    />
                  }
                  label="Include Weekend Reminders"
                />
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quiet Hours
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Pause notifications during specific hours
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.quiet_hours_enabled}
                onChange={(e) => setSettings(prev => ({ ...prev, quiet_hours_enabled: e.target.checked }))}
              />
            }
            label="Enable Quiet Hours"
            sx={{ mb: 2 }}
          />

          {settings.quiet_hours_enabled && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Start Time"
                  type="time"
                  value={settings.quiet_hours_start}
                  onChange={(e) => {
                    setSettings(prev => ({ ...prev, quiet_hours_start: e.target.value }));
                  }}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="End Time"
                  type="time"
                  value={settings.quiet_hours_end}
                  onChange={(e) => {
                    setSettings(prev => ({ ...prev, quiet_hours_end: e.target.value }));
                  }}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Delivery Channels
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Choose how you want to receive notifications
          </Typography>

          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.delivery_channels.in_app}
                  onChange={() => handleToggleDeliveryChannel('in_app')}
                />
              }
              label="In-App Notifications"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.delivery_channels.email}
                  onChange={() => handleToggleDeliveryChannel('email')}
                />
              }
              label="Email Notifications"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.delivery_channels.push}
                  onChange={() => handleToggleDeliveryChannel('push')}
                />
              }
              label="Push Notifications"
            />
          </FormGroup>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          onClick={handleSave}
          disabled={saving}
        >
          Save Settings
        </Button>
      </Box>
    </Container>
  );
};

export default NotificationSettings;
