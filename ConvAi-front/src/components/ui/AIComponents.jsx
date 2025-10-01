import { Box, Card, Typography, useTheme } from "@mui/material";
import { motion } from "framer-motion";
import PropTypes from "prop-types";

const GlassCard = ({
  children,
  elevation = 0,
  hover = true,
  glow = false,
  className = "",
  sx = {},
  ...props
}) => {
  const theme = useTheme();

  const cardVariants = {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    hover: hover ? { y: -2, scale: 1.01 } : {},
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="initial"
      animate="animate"
      whileHover="hover"
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Card
        elevation={elevation}
        className={`glass-card ${className}`}
        sx={{
          background:
            theme.palette.mode === "dark"
              ? "rgba(30, 41, 59, 0.6)"
              : "rgba(255, 255, 255, 0.8)",
          backdropFilter: "blur(20px)",
          border: `1px solid ${
            theme.palette.mode === "dark"
              ? "rgba(148, 163, 184, 0.1)"
              : "rgba(255, 255, 255, 0.2)"
          }`,
          borderRadius: { xs: "8px", sm: "12px", md: "16px" },
          boxShadow:
            theme.palette.mode === "dark"
              ? "0 4px 20px rgba(0, 0, 0, 0.25)"
              : "0 4px 20px rgba(0, 0, 0, 0.08)",
          overflow: "hidden",
          position: "relative",
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          margin: { xs: "4px 0", sm: "6px 0", md: "8px 0" },
          ...(glow && {
            "&:hover": {
              boxShadow:
                theme.palette.mode === "dark"
                  ? "0 12px 25px rgba(99, 102, 241, 0.3)"
                  : "0 12px 25px rgba(79, 70, 229, 0.2)",
            },
          }),
          ...sx,
        }}
        {...props}
      >
        {children}
      </Card>
    </motion.div>
  );
};

GlassCard.propTypes = {
  children: PropTypes.node.isRequired,
  elevation: PropTypes.number,
  hover: PropTypes.bool,
  glow: PropTypes.bool,
  className: PropTypes.string,
  sx: PropTypes.object,
};

const GradientText = ({
  children,
  variant = "h1",
  gradient = "primary",
  className = "",
  sx = {},
  ...props
}) => {
  const gradients = {
    primary: "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
    secondary: "linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%)",
    accent: "linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)",
    rainbow:
      "linear-gradient(135deg, #4f46e5 0%, #06b6d4 25%, #8b5cf6 50%, #ec4899 75%, #f59e0b 100%)",
  };

  return (
    <Typography
      variant={variant}
      className={`gradient-text ${className}`}
      sx={{
        background: gradients[gradient],
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        backgroundClip: "text",
        fontWeight: 700,
        letterSpacing: "-0.02em",
        ...sx,
      }}
      {...props}
    >
      {children}
    </Typography>
  );
};

GradientText.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.string,
  gradient: PropTypes.oneOf(["primary", "secondary", "accent", "rainbow"]),
  className: PropTypes.string,
  sx: PropTypes.object,
};

const FloatingElement = ({
  children,
  delay = 0,
  duration = 3,
  amplitude = 10,
  className = "",
  ...props
}) => {
  return (
    <motion.div
      className={`floating-element ${className}`}
      animate={{
        y: [-amplitude / 2, amplitude / 2, -amplitude / 2],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut",
        delay,
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

FloatingElement.propTypes = {
  children: PropTypes.node.isRequired,
  delay: PropTypes.number,
  duration: PropTypes.number,
  amplitude: PropTypes.number,
  className: PropTypes.string,
};

const NeuralBackground = ({
  opacity = 0.1,
  color = "#4f46e5",
  className = "",
}) => {
  const theme = useTheme();

  return (
    <Box
      className={`neural-background ${className}`}
      sx={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity,
        background: `
          radial-gradient(circle at 20% 80%, ${color}30 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, #06b6d430 0%, transparent 50%),
          radial-gradient(circle at 40% 40%, #8b5cf630 0%, transparent 50%)
        `,
        backgroundImage:
          theme.palette.mode === "dark"
            ? "radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.1) 1px, transparent 0)"
            : "radial-gradient(circle at 2px 2px, rgba(79, 70, 229, 0.1) 1px, transparent 0)",
        backgroundSize: "40px 40px",
        pointerEvents: "none",
        zIndex: -1,
      }}
    />
  );
};

NeuralBackground.propTypes = {
  opacity: PropTypes.number,
  color: PropTypes.string,
  className: PropTypes.string,
};

const AnimatedCounter = ({
  from = 0,
  to,
  duration = 2,
  suffix = "",
  prefix = "",
  className = "",
  ...props
}) => {
  return (
    <motion.span
      className={`animated-counter ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      {...props}
    >
      {prefix}
      <motion.span
        initial={{ textContent: from }}
        animate={{ textContent: to }}
        transition={{ duration, ease: "easeOut" }}
        onUpdate={(latest) => {
          if (latest.textContent !== undefined) {
            latest.textContent = Math.round(latest.textContent);
          }
        }}
      />
      {suffix}
    </motion.span>
  );
};

AnimatedCounter.propTypes = {
  from: PropTypes.number,
  to: PropTypes.number.isRequired,
  duration: PropTypes.number,
  suffix: PropTypes.string,
  prefix: PropTypes.string,
  className: PropTypes.string,
};

// ===== ENHANCED UI COMPONENTS =====

const ShimmerCard = ({ height = 200, className = "", sx = {}, ...props }) => {
  return (
    <Box
      className={`shimmer-card ${className}`}
      sx={{
        height,
        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0.1) 100%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s ease-in-out infinite',
        borderRadius: 2,
        '@keyframes shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        ...sx,
      }}
      {...props}
    />
  );
};

ShimmerCard.propTypes = {
  height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Animated Icon Button with ripple effect
const AnimatedIconButton = ({ 
  children, 
  onClick, 
  color = 'primary',
  size = 'medium',
  className = '',
  sx = {},
  ...props 
}) => {
  const theme = useTheme();
  
  return (
    <motion.button
      className={`animated-icon-button ${className}`}
      onClick={onClick}
      whileHover={{ scale: 1.1, rotate: 5 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      style={{
        padding: size === 'small' ? '8px' : size === 'large' ? '16px' : '12px',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: theme.palette[color]?.main || theme.palette.primary.main,
        position: 'relative',
        overflow: 'hidden',
        ...sx,
      }}
      {...props}
    >
      <motion.div
        initial={{ scale: 0, opacity: 0.5 }}
        whileHover={{ scale: 2, opacity: 0 }}
        transition={{ duration: 0.6 }}
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          background: theme.palette[color]?.main || theme.palette.primary.main,
        }}
      />
      {children}
    </motion.button>
  );
};

AnimatedIconButton.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  color: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Gradient Border Card
const GradientBorderCard = ({ 
  children, 
  borderWidth = 2,
  gradient = 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
  className = '',
  sx = {},
  ...props 
}) => {
  const theme = useTheme();
  
  return (
    <Box
      className={`gradient-border-card ${className}`}
      sx={{
        position: 'relative',
        padding: `${borderWidth}px`,
        background: gradient,
        borderRadius: 3,
        ...sx,
      }}
      {...props}
    >
      <Box
        sx={{
          background: theme.palette.background.paper,
          borderRadius: 2.5,
          height: '100%',
          width: '100%',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

GradientBorderCard.propTypes = {
  children: PropTypes.node.isRequired,
  borderWidth: PropTypes.number,
  gradient: PropTypes.string,
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Pulse Dot Indicator
const PulseDot = ({ 
  color = 'success',
  size = 8,
  className = '',
  sx = {},
  ...props 
}) => {
  const theme = useTheme();
  const dotColor = theme.palette[color]?.main || color;
  
  return (
    <Box
      className={`pulse-dot ${className}`}
      sx={{
        position: 'relative',
        width: size,
        height: size,
        ...sx,
      }}
      {...props}
    >
      <Box
        sx={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          background: dotColor,
          animation: 'pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          '@keyframes pulse-dot': {
            '0%, 100%': {
              opacity: 1,
            },
            '50%': {
              opacity: 0.5,
            },
          },
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          background: dotColor,
          animation: 'pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          '@keyframes pulse-ring': {
            '0%': {
              transform: 'scale(1)',
              opacity: 1,
            },
            '100%': {
              transform: 'scale(2)',
              opacity: 0,
            },
          },
        }}
      />
    </Box>
  );
};

PulseDot.propTypes = {
  color: PropTypes.string,
  size: PropTypes.number,
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Skeleton Loader Component
const SkeletonLoader = ({ 
  variant = 'rectangular',
  width = '100%',
  height = 200,
  borderRadius = 2,
  className = '',
  sx = {},
  ...props 
}) => {
  return (
    <Box
      className={`skeleton-loader ${className}`}
      sx={{
        width,
        height: variant === 'circular' ? width : height,
        borderRadius: variant === 'circular' ? '50%' : borderRadius,
        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0.1) 100%)',
        backgroundSize: '200% 100%',
        animation: 'skeleton-loading 1.5s ease-in-out infinite',
        '@keyframes skeleton-loading': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        ...sx,
      }}
      {...props}
    />
  );
};

SkeletonLoader.propTypes = {
  variant: PropTypes.oneOf(['rectangular', 'circular', 'text']),
  width: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  borderRadius: PropTypes.number,
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Animated Badge with glow
const GlowBadge = ({ 
  children,
  color = 'primary',
  glow = true,
  pulse = false,
  className = '',
  sx = {},
  ...props 
}) => {
  const theme = useTheme();
  const badgeColor = theme.palette[color]?.main || color;
  
  return (
    <motion.div
      className={`glow-badge ${className}`}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      whileHover={{ scale: 1.1 }}
      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
    >
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '4px 12px',
          borderRadius: '999px',
          background: badgeColor,
          color: 'white',
          fontSize: '0.75rem',
          fontWeight: 600,
          boxShadow: glow ? `0 0 20px ${badgeColor}40` : 'none',
          animation: pulse ? 'badge-pulse 2s ease-in-out infinite' : 'none',
          '@keyframes badge-pulse': {
            '0%, 100%': {
              boxShadow: `0 0 20px ${badgeColor}40`,
            },
            '50%': {
              boxShadow: `0 0 30px ${badgeColor}80`,
            },
          },
          ...sx,
        }}
        {...props}
      >
        {children}
      </Box>
    </motion.div>
  );
};

GlowBadge.propTypes = {
  children: PropTypes.node.isRequired,
  color: PropTypes.string,
  glow: PropTypes.bool,
  pulse: PropTypes.bool,
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Animated Progress Ring
const ProgressRing = ({ 
  progress = 0,
  size = 100,
  strokeWidth = 8,
  color = 'primary',
  showPercentage = true,
  className = '',
  sx = {},
  ...props 
}) => {
  const theme = useTheme();
  const ringColor = theme.palette[color]?.main || color;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  
  return (
    <Box
      className={`progress-ring ${className}`}
      sx={{
        position: 'relative',
        width: size,
        height: size,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...sx,
      }}
      {...props}
    >
      <svg
        width={size}
        height={size}
        style={{ transform: 'rotate(-90deg)' }}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}
          strokeWidth={strokeWidth}
          fill="none"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={ringColor}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      {showPercentage && (
        <Typography
          variant="h6"
          sx={{
            position: 'absolute',
            fontWeight: 700,
            color: ringColor,
          }}
        >
          {Math.round(progress)}%
        </Typography>
      )}
    </Box>
  );
};

ProgressRing.propTypes = {
  progress: PropTypes.number,
  size: PropTypes.number,
  strokeWidth: PropTypes.number,
  color: PropTypes.string,
  showPercentage: PropTypes.bool,
  className: PropTypes.string,
  sx: PropTypes.object,
};

// Animated Stat Card
const StatCard = ({ 
  title,
  value,
  icon,
  trend,
  trendValue,
  color = 'primary',
  className = '',
  sx = {},
  ...props 
}) => {
  const theme = useTheme();
  const cardColor = theme.palette[color]?.main || color;
  
  return (
    <motion.div
      className={`stat-card ${className}`}
      whileHover={{ y: -8, boxShadow: `0 12px 24px ${cardColor}20` }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <GlassCard sx={{ ...sx }} {...props}>
        <Box sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              {title}
            </Typography>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                background: `${cardColor}20`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: cardColor,
              }}
            >
              {icon}
            </Box>
          </Box>
          <Typography variant="h4" fontWeight={700} sx={{ mb: 1 }}>
            {value}
          </Typography>
          {trend && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography
                variant="body2"
                sx={{
                  color: trend === 'up' ? theme.palette.success.main : theme.palette.error.main,
                  fontWeight: 600,
                }}
              >
                {trend === 'up' ? '↑' : '↓'} {trendValue}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                from last week
              </Typography>
            </Box>
          )}
        </Box>
      </GlassCard>
    </motion.div>
  );
};

StatCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  icon: PropTypes.node,
  trend: PropTypes.oneOf(['up', 'down']),
  trendValue: PropTypes.string,
  color: PropTypes.string,
  className: PropTypes.string,
  sx: PropTypes.object,
};

export {
  GlassCard,
  GradientText,
  FloatingElement,
  NeuralBackground,
  AnimatedCounter,
  ShimmerCard,
  AnimatedIconButton,
  GradientBorderCard,
  PulseDot,
  SkeletonLoader,
  GlowBadge,
  ProgressRing,
  StatCard,
};
