import { Box, Typography, LinearProgress, Paper, Fade, CircularProgress } from '@mui/material';
import { AutoAwesome, Psychology } from '@mui/icons-material';
import { motion } from 'framer-motion';

/**
 * AI Generation Loading Component
 * Shows an animated loading state when AI is generating content
 */
const AIGeneratingLoader = ({ 
  message = "AI is generating your personalized content...",
  subMessage = "This may take a few moments",
  variant = "full" // "full", "inline", "minimal"
}) => {
  const pulseAnimation = {
    scale: [1, 1.1, 1],
    opacity: [0.7, 1, 0.7],
  };

  if (variant === "minimal") {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <AutoAwesome sx={{ color: 'primary.main', fontSize: 20 }} />
        </motion.div>
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      </Box>
    );
  }

  if (variant === "inline") {
    return (
      <Paper 
        elevation={0} 
        sx={{ 
          p: 2, 
          bgcolor: 'rgba(102, 126, 234, 0.08)', 
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'primary.light'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <motion.div
            animate={pulseAnimation}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <AutoAwesome sx={{ color: 'primary.main', fontSize: 28 }} />
          </motion.div>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body1" fontWeight={600} color="primary.main">
              {message}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {subMessage}
            </Typography>
            <LinearProgress 
              sx={{ 
                mt: 1, 
                borderRadius: 1,
                bgcolor: 'rgba(102, 126, 234, 0.2)',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #667eea, #764ba2)'
                }
              }} 
            />
          </Box>
        </Box>
      </Paper>
    );
  }

  // Full variant (default)
  return (
    <Fade in timeout={500}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 300,
          py: 6,
        }}
      >
        {/* Animated AI Icon */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 5, -5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <Box
            sx={{
              width: 100,
              height: 100,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(102, 126, 234, 0.4)',
              mb: 3,
            }}
          >
            <Psychology sx={{ fontSize: 50, color: 'white' }} />
          </Box>
        </motion.div>

        {/* Sparkles animation */}
        <Box sx={{ position: 'relative', mb: 2 }}>
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              style={{
                position: 'absolute',
                left: `${(i - 1) * 40}px`,
                top: '-20px',
              }}
              animate={{
                y: [0, -10, 0],
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.3,
              }}
            >
              <AutoAwesome sx={{ fontSize: 20, color: 'warning.main' }} />
            </motion.div>
          ))}
        </Box>

        {/* Main message */}
        <Typography 
          variant="h6" 
          fontWeight={700}
          sx={{ 
            mb: 1,
            background: 'linear-gradient(90deg, #667eea, #764ba2)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          ✨ {message}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {subMessage}
        </Typography>

        {/* Progress bar */}
        <Box sx={{ width: '60%', maxWidth: 300 }}>
          <LinearProgress 
            sx={{ 
              height: 6,
              borderRadius: 3,
              bgcolor: 'rgba(102, 126, 234, 0.2)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
                background: 'linear-gradient(90deg, #667eea, #764ba2)',
              }
            }} 
          />
        </Box>

        {/* Telugu message */}
        <Typography 
          variant="caption" 
          sx={{ mt: 2, color: 'text.secondary', fontStyle: 'italic' }}
        >
          మీ కోసం వ్యక్తిగతీకరించిన కంటెంట్‌ను రూపొందిస్తోంది...
        </Typography>
      </Box>
    </Fade>
  );
};

export default AIGeneratingLoader;
