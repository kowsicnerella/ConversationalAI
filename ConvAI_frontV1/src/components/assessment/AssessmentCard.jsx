/**
 * AssessmentCard Component
 * 
 * Displays assessment information in a card format with:
 * - Assessment type and title
 * - Description and metadata
 * - Statistics (completion time, attempts, pass rate)
 * - Action buttons (Start, View Details)
 * - Proficiency level indicator
 * 
 * @component
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  LinearProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Info as InfoIcon,
  Timer as TimerIcon,
  People as PeopleIcon,
  TrendingUp as TrendingIcon,
  EmojiEvents as TrophyIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  getAssessmentTypeInfo,
  getProficiencyInfo,
  formatDuration
} from '../../services/assessmentService';

const AssessmentCard = ({
  assessment,
  onStart,
  onViewDetails,
  statistics = null,
  showActions = true,
  userAttempts = 0,
  lastScore = null,
  isRecommended = false
}) => {
  const typeInfo = getAssessmentTypeInfo(assessment.assessment_type);
  const proficiencyInfo = assessment.proficiency_level
    ? getProficiencyInfo(assessment.proficiency_level)
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          border: isRecommended ? '2px solid' : '1px solid',
          borderColor: isRecommended ? 'primary.main' : 'divider',
          '&:hover': {
            boxShadow: 6,
            transform: 'translateY(-4px)',
            transition: 'all 0.3s ease'
          }
        }}
      >
        {/* Recommended Badge */}
        {isRecommended && (
          <Box
            sx={{
              position: 'absolute',
              top: -10,
              right: 20,
              bgcolor: 'primary.main',
              color: 'white',
              px: 2,
              py: 0.5,
              borderRadius: 2,
              fontSize: '0.75rem',
              fontWeight: 'bold',
              zIndex: 1
            }}
          >
            ⭐ RECOMMENDED
          </Box>
        )}

        <CardContent sx={{ flexGrow: 1, pt: isRecommended ? 3 : 2 }}>
          {/* Assessment Type Badge */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Chip
              icon={<span>{typeInfo.icon}</span>}
              label={typeInfo.label}
              size="small"
              sx={{
                bgcolor: typeInfo.color,
                color: 'white',
                fontWeight: 'bold'
              }}
            />
            
            {assessment.is_adaptive && (
              <Tooltip title="Adaptive test adjusts difficulty in real-time">
                <Chip
                  label="ADAPTIVE"
                  size="small"
                  variant="outlined"
                  color="primary"
                />
              </Tooltip>
            )}

            {proficiencyInfo && (
              <Chip
                icon={<span>{proficiencyInfo.icon}</span>}
                label={proficiencyInfo.label}
                size="small"
                sx={{
                  bgcolor: proficiencyInfo.color,
                  color: 'white'
                }}
              />
            )}
          </Box>

          {/* Title */}
          <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
            {assessment.title}
          </Typography>

          {/* Description */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}
          >
            {assessment.description}
          </Typography>

          {/* Metadata */}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
            {/* Duration */}
            {assessment.duration_minutes && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TimerIcon fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {formatDuration(assessment.duration_minutes)}
                </Typography>
              </Box>
            )}

            {/* Skill Areas */}
            {assessment.skill_areas && assessment.skill_areas.length > 0 && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TrendingIcon fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {assessment.skill_areas.length} skill{assessment.skill_areas.length !== 1 ? 's' : ''}
                </Typography>
              </Box>
            )}

            {/* Certification */}
            {assessment.certification_name && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TrophyIcon fontSize="small" sx={{ color: 'warning.main' }} />
                <Typography variant="caption" fontWeight="bold" color="warning.main">
                  Certification
                </Typography>
              </Box>
            )}
          </Box>

          {/* Statistics (if available) */}
          {statistics && (
            <Box sx={{ bgcolor: 'grey.50', p: 1.5, borderRadius: 1, mb: 2 }}>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Statistics
              </Typography>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
                {statistics.total_attempts !== undefined && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <PeopleIcon fontSize="small" color="primary" />
                      <Typography variant="body2" fontWeight="bold">
                        {statistics.total_attempts}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Attempts
                    </Typography>
                  </Box>
                )}

                {statistics.avg_completion_time && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <TimerIcon fontSize="small" color="info" />
                      <Typography variant="body2" fontWeight="bold">
                        {Math.round(statistics.avg_completion_time)}m
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Avg Time
                    </Typography>
                  </Box>
                )}

                {statistics.question_count !== undefined && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <InfoIcon fontSize="small" color="success" />
                      <Typography variant="body2" fontWeight="bold">
                        {statistics.question_count}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Questions
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>
          )}

          {/* User Progress (if has attempts) */}
          {userAttempts > 0 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Your Progress
                </Typography>
                <Typography variant="caption" fontWeight="bold">
                  {userAttempts} attempt{userAttempts !== 1 ? 's' : ''}
                </Typography>
              </Box>
              
              {lastScore !== null && (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption">Last Score:</Typography>
                    <Typography
                      variant="caption"
                      fontWeight="bold"
                      color={lastScore >= 70 ? 'success.main' : 'error.main'}
                    >
                      {lastScore.toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={lastScore}
                    sx={{
                      height: 6,
                      borderRadius: 1,
                      bgcolor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: lastScore >= 70 ? 'success.main' : 'error.main'
                      }
                    }}
                  />
                </Box>
              )}
            </Box>
          )}

          {/* Passing Score */}
          {assessment.passing_score && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Passing Score: <strong>{assessment.passing_score}%</strong>
              </Typography>
            </Box>
          )}
        </CardContent>

        {/* Actions */}
        {showActions && (
          <CardActions sx={{ p: 2, pt: 0 }}>
            <Button
              variant="contained"
              startIcon={<StartIcon />}
              onClick={() => onStart(assessment)}
              fullWidth
              sx={{ mr: 1 }}
            >
              {userAttempts > 0 ? 'Retake' : 'Start'}
            </Button>
            
            <Tooltip title="View Details">
              <IconButton
                onClick={() => onViewDetails(assessment)}
                color="primary"
              >
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </CardActions>
        )}
      </Card>
    </motion.div>
  );
};

export default AssessmentCard;
