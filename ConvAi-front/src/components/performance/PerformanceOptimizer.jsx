import { useState, useEffect, useCallback, useMemo } from "react";
import {
  Paper,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  Button,
  IconButton,
  Collapse,
  Divider,
  Grid,
  CircularProgress,
} from "@mui/material";
import {
  Speed,
  Settings,
  ExpandMore,
  ExpandLess,
  Refresh,
  Tune,
} from "@mui/icons-material";
import { useTheme } from "@mui/material/styles";

// Performance monitoring utilities
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      fps: 60,
      memoryUsage: 0,
      loadTime: 0,
      renderTime: 0,
      networkLatency: 0,
      cacheHitRate: 0,
    };
    this.observers = [];
    this.isMonitoring = false;
  }

  startMonitoring() {
    if (this.isMonitoring) return;
    this.isMonitoring = true;

    // FPS monitoring
    this.startFPSMonitoring();

    // Memory monitoring
    this.startMemoryMonitoring();

    // Network monitoring
    this.startNetworkMonitoring();

    // Performance observer for paint and layout metrics
    if ("PerformanceObserver" in window) {
      this.setupPerformanceObserver();
    }
  }

  stopMonitoring() {
    this.isMonitoring = false;
    this.observers.forEach((observer) => observer.disconnect());
    this.observers = [];

    if (this.fpsInterval) {
      clearInterval(this.fpsInterval);
    }
    if (this.memoryInterval) {
      clearInterval(this.memoryInterval);
    }
  }

  startFPSMonitoring() {
    let lastTime = performance.now();
    let frames = 0;

    const calculateFPS = () => {
      if (!this.isMonitoring) return;

      frames++;
      const currentTime = performance.now();

      if (currentTime >= lastTime + 1000) {
        this.metrics.fps = Math.round(
          (frames * 1000) / (currentTime - lastTime)
        );
        frames = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(calculateFPS);
    };

    requestAnimationFrame(calculateFPS);
  }

  startMemoryMonitoring() {
    this.memoryInterval = setInterval(() => {
      if ("memory" in performance) {
        const memory = performance.memory;
        this.metrics.memoryUsage = Math.round(
          (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
        );
      }
    }, 1000);
  }

  startNetworkMonitoring() {
    // Monitor connection quality
    if ("connection" in navigator) {
      const connection = navigator.connection;
      this.metrics.networkLatency = this.estimateLatency(
        connection.effectiveType
      );
    }

    // Simulate network requests for latency measurement
    this.measureNetworkLatency();
  }

  estimateLatency(effectiveType) {
    const latencyMap = {
      "slow-2g": 2000,
      "2g": 1400,
      "3g": 670,
      "4g": 0,
    };
    return latencyMap[effectiveType] || 100;
  }

  async measureNetworkLatency() {
    try {
      const start = performance.now();
      await fetch("/api/ping", { method: "HEAD" }).catch(() => {});
      const end = performance.now();
      this.metrics.networkLatency = Math.round(end - start);
    } catch {
      // Simulate latency if no network available
      this.metrics.networkLatency = Math.random() * 200 + 50;
    }

    // Repeat every 30 seconds
    setTimeout(() => this.measureNetworkLatency(), 30000);
  }

  setupPerformanceObserver() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === "paint") {
            if (entry.name === "first-contentful-paint") {
              this.metrics.loadTime = Math.round(entry.startTime);
            }
          } else if (entry.entryType === "measure") {
            if (entry.name.includes("render")) {
              this.metrics.renderTime = Math.round(entry.duration);
            }
          }
        }
      });

      observer.observe({ entryTypes: ["paint", "measure", "navigation"] });
      this.observers.push(observer);
    } catch {
      console.warn("Performance Observer not fully supported");
    }
  }

  getMetrics() {
    return { ...this.metrics };
  }

  // Cache management
  setCacheHitRate(rate) {
    this.metrics.cacheHitRate = rate;
  }
}

const performanceMonitor = new PerformanceMonitor();

// Performance optimization settings
const defaultSettings = {
  enableAnimations: true,
  enableParallax: true,
  enableBlur: true,
  preloadImages: true,
  cacheSize: 50, // MB
  renderQuality: 100, // percentage
  enableLazyLoading: true,
  enableServiceWorker: true,
  autoOptimize: true,
};

const PerformanceOptimizer = () => {
  const theme = useTheme();
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem("performance-settings");
    return saved ? JSON.parse(saved) : defaultSettings;
  });
  const [metrics, setMetrics] = useState(performanceMonitor.getMetrics());
  const [isExpanded, setIsExpanded] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Update metrics every second
  useEffect(() => {
    performanceMonitor.startMonitoring();

    const interval = setInterval(() => {
      setMetrics(performanceMonitor.getMetrics());
    }, 1000);

    return () => {
      clearInterval(interval);
      performanceMonitor.stopMonitoring();
    };
  }, []);

  const applyOptimizations = useCallback((newSettings) => {
    // Apply CSS-based optimizations
    const root = document.documentElement;

    // Animation optimization
    root.style.setProperty(
      "--animation-duration",
      newSettings.enableAnimations ? "0.3s" : "0s"
    );

    // Blur optimization
    root.style.setProperty(
      "--backdrop-blur",
      newSettings.enableBlur ? "blur(20px)" : "none"
    );

    // Render quality
    root.style.setProperty("--render-quality", `${newSettings.renderQuality}%`);

    // Service Worker
    if (newSettings.enableServiceWorker && "serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(console.error);
    }
  }, []);

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem("performance-settings", JSON.stringify(settings));
    applyOptimizations(settings);
  }, [settings, applyOptimizations]);

  const handleSettingChange = (key) => (event) => {
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const autoOptimize = async () => {
    setIsOptimizing(true);

    // Simulate optimization analysis
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const currentMetrics = performanceMonitor.getMetrics();
    const optimizedSettings = { ...settings };

    // Auto-optimize based on performance metrics
    if (currentMetrics.fps < 30) {
      optimizedSettings.enableAnimations = false;
      optimizedSettings.enableParallax = false;
      optimizedSettings.renderQuality = 75;
    }

    if (currentMetrics.memoryUsage > 80) {
      optimizedSettings.cacheSize = Math.max(
        10,
        optimizedSettings.cacheSize * 0.7
      );
      optimizedSettings.preloadImages = false;
    }

    if (currentMetrics.networkLatency > 1000) {
      optimizedSettings.enableLazyLoading = true;
      optimizedSettings.preloadImages = false;
    }

    setSettings(optimizedSettings);
    setIsOptimizing(false);
  };

  const resetToDefaults = () => {
    setSettings(defaultSettings);
  };

  const getPerformanceColor = (value, thresholds) => {
    if (value >= thresholds.good) return theme.palette.success.main;
    if (value >= thresholds.ok) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getMemoryColor = (usage) => {
    if (usage < 50) return theme.palette.success.main;
    if (usage < 80) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const performanceScore = useMemo(() => {
    const fpsScore = Math.min(metrics.fps / 60, 1) * 25;
    const memoryScore = Math.max(0, (100 - metrics.memoryUsage) / 100) * 25;
    const loadScore = Math.max(0, (3000 - metrics.loadTime) / 3000) * 25;
    const networkScore =
      Math.max(0, (1000 - metrics.networkLatency) / 1000) * 25;

    return Math.round(fpsScore + memoryScore + loadScore + networkScore);
  }, [metrics]);

  const getScoreColor = (score) => {
    if (score >= 80) return theme.palette.success.main;
    if (score >= 60) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  return (
    <Paper
      sx={{
        p: 2,
        background:
          theme.palette.mode === "dark"
            ? "rgba(30, 41, 59, 0.8)"
            : "rgba(255, 255, 255, 0.8)",
        backdropFilter: "blur(20px)",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        borderRadius: 3,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          mb: 2,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              background: "rgba(79, 70, 229, 0.2)",
              color: theme.palette.primary.main,
            }}
          >
            <Speed />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Performance Monitor
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Overall Score: {performanceScore}/100
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <CircularProgress
            variant="determinate"
            value={performanceScore}
            size={40}
            thickness={4}
            sx={{
              color: getScoreColor(performanceScore),
              "& .MuiCircularProgress-circle": {
                strokeLinecap: "round",
              },
            }}
          />
          <IconButton onClick={() => setIsExpanded(!isExpanded)} sx={{ ml: 1 }}>
            {isExpanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
      </Box>

      {/* Performance Metrics */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 600,
                color: getPerformanceColor(metrics.fps, { good: 50, ok: 30 }),
              }}
            >
              {metrics.fps}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              FPS
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 600,
                color: getMemoryColor(metrics.memoryUsage),
              }}
            >
              {metrics.memoryUsage}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Memory
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 600,
                color: getPerformanceColor(metrics.loadTime, {
                  good: 1000,
                  ok: 2000,
                }),
              }}
            >
              {metrics.loadTime}ms
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Load Time
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 600,
                color: getPerformanceColor(metrics.networkLatency, {
                  good: 100,
                  ok: 500,
                }),
              }}
            >
              {metrics.networkLatency}ms
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Network
            </Typography>
          </Box>
        </Grid>
      </Grid>

      {/* Auto-optimize button */}
      <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
        <Button
          variant="contained"
          onClick={autoOptimize}
          disabled={isOptimizing}
          startIcon={isOptimizing ? <CircularProgress size={16} /> : <Tune />}
          sx={{
            background: "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
            "&:hover": {
              background: "linear-gradient(135deg, #4338ca 0%, #0891b2 100%)",
            },
          }}
        >
          {isOptimizing ? "optimizing..." : "Auto Optimize"}
        </Button>
        <Button
          variant="outlined"
          onClick={resetToDefaults}
          startIcon={<Refresh />}
        >
          Reset
        </Button>
      </Box>

      {/* Performance Tips */}
      {performanceScore < 70 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Performance Suggestions:
          </Typography>
          <Typography variant="body2">
            {metrics.fps < 30 && "• Disable animations and parallax effects. "}
            {metrics.memoryUsage > 80 &&
              "• Reduce cache size and disable image preloading. "}
            {metrics.networkLatency > 1000 &&
              "• Enable lazy loading for better network performance. "}
          </Typography>
        </Alert>
      )}

      {/* Expandable Settings */}
      <Collapse in={isExpanded}>
        <Divider sx={{ my: 2 }} />

        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Optimization Settings
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enableAnimations}
                  onChange={handleSettingChange("enableAnimations")}
                />
              }
              label="Enable Animations"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enableParallax}
                  onChange={handleSettingChange("enableParallax")}
                />
              }
              label="Enable Parallax Effects"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enableBlur}
                  onChange={handleSettingChange("enableBlur")}
                />
              }
              label="Enable Backdrop Blur"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.preloadImages}
                  onChange={handleSettingChange("preloadImages")}
                />
              }
              label="Preload Images"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enableLazyLoading}
                  onChange={handleSettingChange("enableLazyLoading")}
                />
              }
              label="Enable Lazy Loading"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enableServiceWorker}
                  onChange={handleSettingChange("enableServiceWorker")}
                />
              }
              label="Enable Service Worker"
            />
          </Grid>
        </Grid>

        {/* Advanced Settings */}
        <Box sx={{ mt: 2 }}>
          <Button
            onClick={() => setShowAdvanced(!showAdvanced)}
            startIcon={<Settings />}
            size="small"
          >
            Advanced Settings
          </Button>

          <Collapse in={showAdvanced}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Cache Size: {settings.cacheSize} MB
              </Typography>
              <Slider
                value={settings.cacheSize}
                onChange={(_, value) =>
                  setSettings((prev) => ({ ...prev, cacheSize: value }))
                }
                min={10}
                max={200}
                marks={[
                  { value: 10, label: "10MB" },
                  { value: 50, label: "50MB" },
                  { value: 100, label: "100MB" },
                  { value: 200, label: "200MB" },
                ]}
                sx={{ mt: 1, mb: 2 }}
              />

              <Typography variant="subtitle2" gutterBottom>
                Render Quality: {settings.renderQuality}%
              </Typography>
              <Slider
                value={settings.renderQuality}
                onChange={(_, value) =>
                  setSettings((prev) => ({ ...prev, renderQuality: value }))
                }
                min={25}
                max={100}
                marks={[
                  { value: 25, label: "25%" },
                  { value: 50, label: "50%" },
                  { value: 75, label: "75%" },
                  { value: 100, label: "100%" },
                ]}
                sx={{ mt: 1 }}
              />
            </Box>
          </Collapse>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default PerformanceOptimizer;
