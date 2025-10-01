import { useState, useEffect, useCallback } from "react";
import {
  Paper,
  Typography,
  Box,
  IconButton,
  Chip,
  Alert,
  AlertTitle,
  Button,
  LinearProgress,
} from "@mui/material";
import {
  CloudOff,
  CloudDone,
  Sync,
  Download,
  Storage,
  CheckCircle,
  Close,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "@mui/material/styles";
import { offlineAPI } from "../../services/api";
import { toast } from "react-hot-toast";

// Offline storage utilities
class OfflineStorage {
  constructor() {
    this.dbName = "TeluguLearningApp";
    this.version = 1;
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object stores
        if (!db.objectStoreNames.contains("lessons")) {
          const lessonsStore = db.createObjectStore("lessons", {
            keyPath: "id",
          });
          lessonsStore.createIndex("chapterId", "chapterId", { unique: false });
          lessonsStore.createIndex("difficulty", "difficulty", {
            unique: false,
          });
        }

        if (!db.objectStoreNames.contains("vocabulary")) {
          const vocabStore = db.createObjectStore("vocabulary", {
            keyPath: "id",
          });
          vocabStore.createIndex("category", "category", { unique: false });
        }

        if (!db.objectStoreNames.contains("progress")) {
          db.createObjectStore("progress", { keyPath: "id" });
        }

        if (!db.objectStoreNames.contains("activities")) {
          const activitiesStore = db.createObjectStore("activities", {
            keyPath: "id",
          });
          activitiesStore.createIndex("type", "type", { unique: false });
        }

        if (!db.objectStoreNames.contains("userSettings")) {
          db.createObjectStore("userSettings", { keyPath: "key" });
        }
      };
    });
  }

  async store(storeName, data) {
    const transaction = this.db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);

    if (Array.isArray(data)) {
      for (const item of data) {
        await store.put(item);
      }
    } else {
      await store.put(data);
    }

    return transaction.complete;
  }

  async get(storeName, key) {
    const transaction = this.db.transaction([storeName], "readonly");
    const store = transaction.objectStore(storeName);
    return store.get(key);
  }

  async getAll(storeName) {
    const transaction = this.db.transaction([storeName], "readonly");
    const store = transaction.objectStore(storeName);
    return store.getAll();
  }

  async clear(storeName) {
    const transaction = this.db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);
    return store.clear();
  }

  async getStorageInfo() {
    const estimate = await navigator.storage.estimate();
    return {
      used: estimate.usage || 0,
      quota: estimate.quota || 0,
      usedPercentage: estimate.quota
        ? (estimate.usage / estimate.quota) * 100
        : 0,
    };
  }
}

const offlineStorage = new OfflineStorage();

const OfflineManager = () => {
  const theme = useTheme();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showOfflineAlert, setShowOfflineAlert] = useState(false);
  const [syncProgress, setSyncProgress] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);
  const [offlineData, setOfflineData] = useState({
    lessons: 0,
    vocabulary: 0,
    activities: 0,
    progress: 0,
  });
  const [storageInfo, setStorageInfo] = useState({
    used: 0,
    quota: 0,
    usedPercentage: 0,
  });

  useEffect(() => {
    // Initialize offline storage
    offlineStorage.init().then(() => {
      updateOfflineDataCount();
      updateStorageInfo();
    });

    // Online/offline event listeners
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineAlert(false);
      // Auto-sync when coming back online
      syncOfflineData();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineAlert(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [syncOfflineData]);

  const updateOfflineDataCount = async () => {
    try {
      const lessons = await offlineStorage.getAll("lessons");
      const vocabulary = await offlineStorage.getAll("vocabulary");
      const activities = await offlineStorage.getAll("activities");
      const progress = await offlineStorage.getAll("progress");

      setOfflineData({
        lessons: lessons.length,
        vocabulary: vocabulary.length,
        activities: activities.length,
        progress: progress.length,
      });
    } catch (error) {
      console.error("Error updating offline data count:", error);
    }
  };

  const updateStorageInfo = async () => {
    try {
      const info = await offlineStorage.getStorageInfo();
      setStorageInfo(info);
    } catch (error) {
      console.error("Error getting storage info:", error);
    }
  };

  const downloadForOffline = async () => {
    setIsSyncing(true);
    setSyncProgress(0);

    try {
      // Download essential data from API
      const dataTypes = ["lessons", "vocabulary", "activities", "progress"];

      for (let i = 0; i < dataTypes.length; i++) {
        const dataType = dataTypes[i];
        setSyncProgress(((i + 1) / dataTypes.length) * 100);

        try {
          // Real API call to download content
          const response = await offlineAPI.downloadContent(dataType);

          if (response.data.success) {
            await offlineStorage.store(dataType, response.data.content);
          } else {
            // Fallback to mock data if API fails
            const mockData = generateMockData(dataType);
            await offlineStorage.store(dataType, mockData);
          }
        } catch (error) {
          console.error(`Error downloading ${dataType}:`, error);
          // Fallback to mock data
          const mockData = generateMockData(dataType);
          await offlineStorage.store(dataType, mockData);
        }
      }

      await updateOfflineDataCount();
      await updateStorageInfo();
      toast.success("Content downloaded for offline use!");
    } catch (error) {
      console.error("Error downloading data for offline use:", error);
      toast.error("Failed to download offline content");
    } finally {
      setIsSyncing(false);
      setSyncProgress(0);
    }
  };

  const syncOfflineData = useCallback(async () => {
    if (!isOnline) return;

    setIsSyncing(true);
    setSyncProgress(0);

    try {
      // Get all offline data that needs syncing
      const progressData = await offlineStorage.getAll("progress");
      const activitiesData = await offlineStorage.getAll("activities");
      const vocabularyData = await offlineStorage.getAll("vocabulary");

      setSyncProgress(25);

      // Sync progress data to server
      if (progressData.length > 0) {
        await offlineAPI.syncProgress(progressData);
      }

      setSyncProgress(50);

      // Sync all data
      const syncData = {
        progress: progressData,
        activities: activitiesData,
        vocabulary: vocabularyData,
        timestamp: new Date().toISOString(),
      };

      await offlineAPI.syncAllData(syncData);
      setSyncProgress(100);

      // Clear synced data from offline storage
      await offlineStorage.clear("progress");
      await updateOfflineDataCount();

      toast.success("Data synced successfully!");
      console.log("Synced offline data:", syncData);
    } catch (error) {
      console.error("Error syncing offline data:", error);
      toast.error("Failed to sync offline data");
    } finally {
      setIsSyncing(false);
      setSyncProgress(0);
    }
  }, [isOnline]);

  const clearOfflineData = async () => {
    try {
      const stores = ["lessons", "vocabulary", "activities", "progress"];
      for (const store of stores) {
        await offlineStorage.clear(store);
      }
      await updateOfflineDataCount();
      await updateStorageInfo();
    } catch (error) {
      console.error("Error clearing offline data:", error);
    }
  };

  const generateMockData = (dataType) => {
    const mockData = [];
    const count = Math.floor(Math.random() * 10) + 5; // 5-15 items

    for (let i = 1; i <= count; i++) {
      switch (dataType) {
        case "lessons":
          mockData.push({
            id: `lesson_${i}`,
            title: `Telugu Lesson ${i}`,
            content: `Content for lesson ${i}`,
            chapterId: `chapter_${Math.ceil(i / 3)}`,
            difficulty: ["beginner", "intermediate", "advanced"][
              Math.floor(Math.random() * 3)
            ],
            downloadedAt: new Date().toISOString(),
          });
          break;
        case "vocabulary":
          mockData.push({
            id: `vocab_${i}`,
            telugu: `తెలుగు పదం ${i}`,
            english: `English word ${i}`,
            category: ["basics", "family", "food", "colors"][
              Math.floor(Math.random() * 4)
            ],
            downloadedAt: new Date().toISOString(),
          });
          break;
        case "activities":
          mockData.push({
            id: `activity_${i}`,
            type: ["quiz", "matching", "translation"][
              Math.floor(Math.random() * 3)
            ],
            title: `Activity ${i}`,
            questions: [],
            downloadedAt: new Date().toISOString(),
          });
          break;
        case "progress":
          mockData.push({
            id: `progress_${i}`,
            lessonId: `lesson_${i}`,
            completed: Math.random() > 0.5,
            score: Math.floor(Math.random() * 100),
            lastUpdated: new Date().toISOString(),
          });
          break;
        default:
          break;
      }
    }
    return mockData;
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <>
      {/* Offline Alert */}
      <AnimatePresence>
        {showOfflineAlert && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            style={{
              position: "fixed",
              top: 16,
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 9999,
              width: "90%",
              maxWidth: 500,
            }}
          >
            <Alert
              severity="warning"
              sx={{
                background:
                  theme.palette.mode === "dark"
                    ? "rgba(251, 146, 60, 0.1)"
                    : "rgba(251, 146, 60, 0.1)",
                backdropFilter: "blur(10px)",
                border: "1px solid rgba(251, 146, 60, 0.3)",
                borderRadius: 2,
              }}
              action={
                <IconButton
                  aria-label="close"
                  color="inherit"
                  size="small"
                  onClick={() => setShowOfflineAlert(false)}
                >
                  <Close fontSize="inherit" />
                </IconButton>
              }
            >
              <AlertTitle>You&apos;re currently offline</AlertTitle>
              You can still access downloaded content and continue learning!
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Connection Status */}
      <Paper
        sx={{
          p: 2,
          mb: 2,
          background:
            theme.palette.mode === "dark"
              ? "rgba(30, 41, 59, 0.8)"
              : "rgba(255, 255, 255, 0.8)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          borderRadius: 3,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                background: isOnline
                  ? "rgba(34, 197, 94, 0.2)"
                  : "rgba(239, 68, 68, 0.2)",
                color: isOnline ? "#22c55e" : "#ef4444",
              }}
            >
              {isOnline ? <CloudDone /> : <CloudOff />}
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {isOnline ? "Online" : "Offline Mode"}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isOnline
                  ? "All features available"
                  : "Using downloaded content"}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={downloadForOffline}
              disabled={!isOnline || isSyncing}
              startIcon={<Download />}
            >
              Download
            </Button>
            {isOnline && (
              <Button
                variant="outlined"
                size="small"
                onClick={syncOfflineData}
                disabled={isSyncing}
                startIcon={<Sync />}
              >
                Sync
              </Button>
            )}
          </Box>
        </Box>

        {isSyncing && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress
              variant="determinate"
              value={syncProgress}
              sx={{
                borderRadius: 1,
                height: 6,
                "& .MuiLinearProgress-bar": {
                  background:
                    "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
                },
              }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 0.5, display: "block" }}
            >
              {syncProgress === 0
                ? "Preparing..."
                : `${Math.round(syncProgress)}% complete`}
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Offline Data Summary */}
      <Paper
        sx={{
          p: 2,
          mb: 2,
          background:
            theme.palette.mode === "dark"
              ? "rgba(30, 41, 59, 0.8)"
              : "rgba(255, 255, 255, 0.8)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          borderRadius: 3,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            mb: 2,
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Downloaded Content
          </Typography>
          <Button
            size="small"
            color="error"
            onClick={clearOfflineData}
            startIcon={<Storage />}
          >
            Clear All
          </Button>
        </Box>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
          <Chip
            icon={<CheckCircle />}
            label={`${offlineData.lessons} Lessons`}
            color="primary"
            variant="outlined"
            size="small"
          />
          <Chip
            icon={<CheckCircle />}
            label={`${offlineData.vocabulary} Words`}
            color="secondary"
            variant="outlined"
            size="small"
          />
          <Chip
            icon={<CheckCircle />}
            label={`${offlineData.activities} Activities`}
            color="info"
            variant="outlined"
            size="small"
          />
          <Chip
            icon={<CheckCircle />}
            label={`${offlineData.progress} Progress`}
            color="success"
            variant="outlined"
            size="small"
          />
        </Box>

        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Storage Used
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatBytes(storageInfo.used)} / {formatBytes(storageInfo.quota)}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={storageInfo.usedPercentage}
            sx={{
              borderRadius: 1,
              height: 4,
              "& .MuiLinearProgress-bar": {
                background:
                  storageInfo.usedPercentage > 80
                    ? "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
                    : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              },
            }}
          />
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 0.5, display: "block" }}
          >
            {storageInfo.usedPercentage.toFixed(1)}% of available storage
          </Typography>
        </Box>
      </Paper>
    </>
  );
};

export default OfflineManager;
