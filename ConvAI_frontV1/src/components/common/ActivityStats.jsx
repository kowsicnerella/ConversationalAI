import PropTypes from "prop-types";
import {
  Box,
  Stack,
  Typography,
  LinearProgress,
  useTheme,
} from "@mui/material";
import {
  Timer,
  EmojiEvents,
  CheckCircle,
  Person,
  TrendingUp,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const ActivityStats = ({ stats, showProgress = true }) => {
  const theme = useTheme();

  const StatItem = ({ icon: Icon, label, value, color, progress }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Box>
        <Stack
          direction="row"
          alignItems="center"
          spacing={1}
          mb={progress !== undefined ? 0.5 : 0}
        >
          <Icon sx={{ fontSize: 20, color: color || "action.active" }} />
          <Typography variant="body2" color="text.secondary">
            {label}
          </Typography>
          <Typography variant="body2" fontWeight={600} ml="auto">
            {value}
          </Typography>
        </Stack>
        {progress !== undefined && showProgress && (
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 6,
              borderRadius: 3,
              background: theme.palette.action.hover,
              "& .MuiLinearProgress-bar": {
                background: color || theme.palette.primary.main,
              },
            }}
          />
        )}
      </Box>
    </motion.div>
  );

  return (
    <Stack spacing={2}>
      {stats.averageScore !== undefined && (
        <StatItem
          icon={EmojiEvents}
          label="Average Score"
          value={`${stats.averageScore}%`}
          progress={stats.averageScore}
          color={theme.palette.warning.main}
        />
      )}

      {stats.completionRate !== undefined && (
        <StatItem
          icon={CheckCircle}
          label="Completion Rate"
          value={`${stats.completionRate}%`}
          progress={stats.completionRate}
          color={theme.palette.success.main}
        />
      )}

      {stats.totalAttempts !== undefined && (
        <StatItem
          icon={Person}
          label="Total Attempts"
          value={stats.totalAttempts.toLocaleString()}
          color={theme.palette.info.main}
        />
      )}

      {stats.averageTimeSpent !== undefined && (
        <StatItem
          icon={Timer}
          label="Avg. Time Spent"
          value={`${stats.averageTimeSpent} min`}
          color={theme.palette.secondary.main}
        />
      )}

      {stats.progressPercentage !== undefined && (
        <StatItem
          icon={TrendingUp}
          label="Your Progress"
          value={`${stats.progressPercentage}%`}
          progress={stats.progressPercentage}
          color={theme.palette.primary.main}
        />
      )}
    </Stack>
  );
};

ActivityStats.propTypes = {
  stats: PropTypes.shape({
    averageScore: PropTypes.number,
    completionRate: PropTypes.number,
    totalAttempts: PropTypes.number,
    averageTimeSpent: PropTypes.number,
    progressPercentage: PropTypes.number,
  }).isRequired,
  showProgress: PropTypes.bool,
};

export default ActivityStats;
