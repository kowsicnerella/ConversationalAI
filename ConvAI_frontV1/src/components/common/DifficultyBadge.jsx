import PropTypes from "prop-types";
import { Chip, alpha, useTheme } from "@mui/material";
import { TrendingUp, TrendingFlat, TrendingDown } from "@mui/icons-material";

const DifficultyBadge = ({ difficulty, size = "small", showIcon = false }) => {
  const theme = useTheme();

  const getDifficultyConfig = (level) => {
    switch (level.toLowerCase()) {
      case "beginner":
        return {
          color: theme.palette.success.main,
          label: "Beginner",
          icon: TrendingDown,
        };
      case "intermediate":
        return {
          color: theme.palette.warning.main,
          label: "Intermediate",
          icon: TrendingFlat,
        };
      case "advanced":
        return {
          color: theme.palette.error.main,
          label: "Advanced",
          icon: TrendingUp,
        };
      default:
        return {
          color: theme.palette.grey[500],
          label: difficulty,
          icon: TrendingFlat,
        };
    }
  };

  const config = getDifficultyConfig(difficulty);
  const IconComponent = config.icon;

  return (
    <Chip
      icon={showIcon ? <IconComponent /> : undefined}
      label={config.label}
      size={size}
      sx={{
        fontWeight: 600,
        background: alpha(config.color, 0.1),
        color: config.color,
        border: `1px solid ${alpha(config.color, 0.3)}`,
        "& .MuiChip-icon": {
          color: config.color,
        },
      }}
    />
  );
};

DifficultyBadge.propTypes = {
  difficulty: PropTypes.string.isRequired,
  size: PropTypes.oneOf(["small", "medium"]),
  showIcon: PropTypes.bool,
};

export default DifficultyBadge;
