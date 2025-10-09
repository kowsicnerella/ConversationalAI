import PropTypes from "prop-types";
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Stack,
  Chip,
  Box,
  useTheme,
  alpha,
} from "@mui/material";
import {
  Style,
  Quiz,
  MenuBook,
  Psychology,
  Timer,
  PlayArrow,
  CheckCircle,
  Star,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import AnimatedButton from "./AnimatedButton";

const ActivityCard = ({ activity, onClick, compact = false }) => {
  const theme = useTheme();

  const getActivityIcon = (type) => {
    switch (type) {
      case "flashcard":
        return Style;
      case "quiz":
        return Quiz;
      case "reading":
        return MenuBook;
      default:
        return Psychology;
    }
  };

  const getActivityTypeLabel = (type) => {
    switch (type) {
      case "flashcard":
        return "Flashcards";
      case "quiz":
        return "Quiz";
      case "reading":
        return "Reading";
      default:
        return type;
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "beginner":
        return "success";
      case "intermediate":
        return "warning";
      case "advanced":
        return "error";
      default:
        return "default";
    }
  };

  const IconComponent = getActivityIcon(activity.type);
  const activityColor = activity.color || theme.palette.primary.main;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          position: "relative",
          overflow: "visible",
          cursor: "pointer",
          transition: "all 0.3s ease",
          background:
            theme.palette.mode === "dark"
              ? `linear-gradient(135deg, ${alpha(
                  activityColor,
                  0.1
                )} 0%, ${alpha(theme.palette.background.paper, 0.9)} 100%)`
              : theme.palette.background.paper,
          backdropFilter: "blur(10px)",
          border: `1px solid ${alpha(activityColor, 0.2)}`,
          "&:hover": {
            boxShadow: `0 12px 40px ${alpha(activityColor, 0.3)}`,
            border: `1px solid ${alpha(activityColor, 0.5)}`,
          },
        }}
        onClick={onClick}
      >
        {/* Progress indicator */}
        {activity.progress > 0 && (
          <Box
            sx={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: 4,
              background: `linear-gradient(90deg, ${activityColor} 0%, ${alpha(
                activityColor,
                0.5
              )} 100%)`,
              width: `${activity.progress}%`,
              transition: "width 0.3s ease",
            }}
          />
        )}

        {/* Completed badge */}
        {activity.completed && (
          <Chip
            icon={<CheckCircle />}
            label={`Score: ${activity.score}%`}
            color="success"
            size="small"
            sx={{
              position: "absolute",
              top: 12,
              right: 12,
              zIndex: 1,
              fontWeight: 600,
            }}
          />
        )}

        <CardContent sx={{ flexGrow: 1, pt: activity.completed ? 5 : 2 }}>
          {/* Icon & Type */}
          <Stack direction="row" spacing={2} alignItems="center" mb={2}>
            <Box
              sx={{
                p: compact ? 1 : 1.5,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${alpha(
                  activityColor,
                  0.2
                )}, ${alpha(activityColor, 0.1)})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <IconComponent
                sx={{ color: activityColor, fontSize: compact ? 24 : 28 }}
              />
            </Box>
            <Chip
              label={getActivityTypeLabel(activity.type)}
              size="small"
              sx={{
                fontWeight: 600,
                background: alpha(activityColor, 0.1),
                color: activityColor,
              }}
            />
          </Stack>

          {/* Title */}
          <Typography
            variant={compact ? "subtitle1" : "h6"}
            sx={{
              fontWeight: 700,
              mb: 1,
              color: theme.palette.text.primary,
            }}
          >
            {activity.title}
          </Typography>

          {/* Description */}
          {!compact && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                mb: 2,
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
                minHeight: 40,
              }}
            >
              {activity.description}
            </Typography>
          )}

          {/* Stats */}
          <Stack direction="row" spacing={1} mb={2} flexWrap="wrap" gap={1}>
            <Chip
              icon={<Timer />}
              label={`${activity.estimatedTime} min`}
              size="small"
              variant="outlined"
            />
            <Chip
              label={activity.difficulty}
              size="small"
              color={getDifficultyColor(activity.difficulty)}
            />
            {activity.wordsCount && (
              <Chip
                label={`${activity.wordsCount} words`}
                size="small"
                variant="outlined"
              />
            )}
            {activity.questionsCount && (
              <Chip
                label={`${activity.questionsCount} questions`}
                size="small"
                variant="outlined"
              />
            )}
          </Stack>

          {/* Tags */}
          {activity.tags && !compact && (
            <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
              {activity.tags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: "0.7rem", height: 20 }}
                />
              ))}
            </Stack>
          )}
        </CardContent>

        <CardActions sx={{ p: 2, pt: 0 }}>
          <AnimatedButton
            fullWidth
            variant={activity.completed ? "outlined" : "contained"}
            startIcon={activity.completed ? <Star /> : <PlayArrow />}
            sx={{
              background: !activity.completed
                ? `linear-gradient(135deg, ${activityColor}, ${alpha(
                    activityColor,
                    0.7
                  )})`
                : "transparent",
              color: !activity.completed ? "#fff" : theme.palette.text.primary,
            }}
          >
            {activity.completed
              ? "Practice Again"
              : activity.progress > 0
              ? "Continue"
              : "Start Activity"}
          </AnimatedButton>
        </CardActions>
      </Card>
    </motion.div>
  );
};

ActivityCard.propTypes = {
  activity: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    type: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    difficulty: PropTypes.string.isRequired,
    estimatedTime: PropTypes.number.isRequired,
    wordsCount: PropTypes.number,
    questionsCount: PropTypes.number,
    completed: PropTypes.bool,
    progress: PropTypes.number,
    score: PropTypes.number,
    color: PropTypes.string,
    tags: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  onClick: PropTypes.func,
  compact: PropTypes.bool,
};

export default ActivityCard;
