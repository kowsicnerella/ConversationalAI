import React from "react";
import { Container, Typography, Box, Tabs, Tab } from "@mui/material";
import {
  Settings as SettingsIcon,
  CloudOff,
  Speed,
  Notifications,
  Palette,
  Security,
  Help,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useTheme } from "@mui/material/styles";
import { GlassCard, GradientText } from "../components/ui/AIComponents";
import NotificationSystem from "../components/notifications/NotificationSystem";
import OfflineManager from "../components/offline/OfflineManager";
import PerformanceOptimizer from "../components/performance/PerformanceOptimizer";
import PropTypes from "prop-types";

const TabPanel = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

const SettingsPage = () => {
  const theme = useTheme();
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const tabItems = [
    {
      icon: <Notifications />,
      label: "Notifications",
      component: <NotificationSystem />,
    },
    {
      icon: <CloudOff />,
      label: "Offline Mode",
      component: <OfflineManager />,
    },
    {
      icon: <Speed />,
      label: "Performance",
      component: <PerformanceOptimizer />,
    },
    {
      icon: <Palette />,
      label: "Appearance",
      component: <Box>Theme settings coming soon...</Box>,
    },
    {
      icon: <Security />,
      label: "Privacy",
      component: <Box>Privacy settings coming soon...</Box>,
    },
    {
      icon: <Help />,
      label: "Help",
      component: <Box>Help documentation coming soon...</Box>,
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4, textAlign: "center" }}>
          <Box
            sx={{
              display: "inline-flex",
              p: 2,
              borderRadius: 3,
              background:
                "linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%)",
              mb: 2,
            }}
          >
            <SettingsIcon
              sx={{ fontSize: 40, color: theme.palette.primary.main }}
            />
          </Box>
          <GradientText variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
            Settings
          </GradientText>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ maxWidth: 600, mx: "auto" }}
          >
            Customize your learning experience with advanced features and
            optimizations
          </Typography>
        </Box>

        {/* Settings Content */}
        <GlassCard>
          <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 0 }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                "& .MuiTab-root": {
                  minWidth: 120,
                  fontWeight: 500,
                  textTransform: "none",
                  "&.Mui-selected": {
                    background:
                      "linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%)",
                    borderRadius: "8px 8px 0 0",
                  },
                },
                "& .MuiTabs-indicator": {
                  background:
                    "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
                  height: 3,
                  borderRadius: "3px 3px 0 0",
                },
              }}
            >
              {tabItems.map((item, index) => (
                <Tab
                  key={index}
                  icon={item.icon}
                  label={item.label}
                  iconPosition="start"
                  sx={{ gap: 1 }}
                />
              ))}
            </Tabs>
          </Box>

          {/* Tab Panels */}
          {tabItems.map((item, index) => (
            <TabPanel key={index} value={tabValue} index={index}>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                {item.component}
              </motion.div>
            </TabPanel>
          ))}
        </GlassCard>
      </motion.div>
    </Container>
  );
};

export default SettingsPage;
