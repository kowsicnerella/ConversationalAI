/**
 * CertificationPrepDashboard Component
 * 
 * Comprehensive certification preparation dashboard with:
 * - Readiness gauge
 * - Missing skills checklist
 * - Recommended study path
 * - Practice test suggestions
 * - Progress tracking
 * 
 * @component
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  Alert,
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  CheckCircle as CompletedIcon,
  RadioButtonUnchecked as IncompleteIcon,
  TrendingUp as ProgressIcon,
  School as CertIcon,
  EmojiEvents as TrophyIcon,
  Warning as WarningIcon,
  PlayArrow as StartIcon,
  ExpandMore as ExpandIcon,
  Lightbulb as TipIcon
} from '@mui/icons-material';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import {
  checkCertificationReadiness,
  getRecommendations,
  getProficiencyInfo
} from '../../services/assessmentService';

const CertificationPrepDashboard = ({ userId, certificationName }) => {
  const [loading, setLoading] = useState(true);
  const [readiness, setReadiness] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [userId, certificationName]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load certification readiness
      const readinessResponse = await checkCertificationReadiness(certificationName);
      if (readinessResponse.success) {
        setReadiness(readinessResponse.readiness);
      }

      // Load recommendations
      const recsResponse = await getRecommendations();
      if (recsResponse.success) {
        setRecommendations(recsResponse.recommendations);
      }
    } catch (err) {
      setError(err.message || 'Failed to load certification data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!readiness) {
    return (
      <Alert severity="info">
        No certification readiness data available. Complete some assessments to get started.
      </Alert>
    );
  }

  const readyPercentage = readiness.ready ? 100 : readiness.readiness_percentage || 0;
  const isReady = readiness.ready;
  const missingSkills = readiness.missing_skills || [];
  const strengthSkills = readiness.strength_skills || [];
  const recommendedActions = readiness.recommended_actions || [];

  return (
    <Box>
      {/* Readiness Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Readiness Gauge */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                <CertIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                Certification Readiness
              </Typography>
              
              <Box sx={{ width: 200, height: 200, mx: 'auto', my: 3 }}>
                <CircularProgressbar
                  value={readyPercentage}
                  text={`${readyPercentage.toFixed(0)}%`}
                  styles={buildStyles({
                    textSize: '16px',
                    pathColor: isReady ? '#4caf50' : readyPercentage >= 70 ? '#ff9800' : '#f44336',
                    textColor: '#333',
                    trailColor: '#e0e0e0'
                  })}
                />
              </Box>

              {isReady ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  <strong>You&apos;re Ready!</strong> You can take the certification exam.
                </Alert>
              ) : (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <strong>Keep Practicing!</strong> {missingSkills.length} skills need improvement.
                </Alert>
              )}

              <Typography variant="body2" color="text.secondary">
                {certificationName}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Skills Summary */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Skills Overview
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Paper sx={{ p: 2, bgcolor: 'success.50', textAlign: 'center' }}>
                    <Typography variant="h3" color="success.main" fontWeight="bold">
                      {strengthSkills.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Strengths
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={6}>
                  <Paper sx={{ p: 2, bgcolor: 'error.50', textAlign: 'center' }}>
                    <Typography variant="h3" color="error.main" fontWeight="bold">
                      {missingSkills.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Needs Work
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Required Proficiency */}
              {readiness.required_proficiency && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Required Proficiency Level
                  </Typography>
                  <Chip
                    icon={<span>{getProficiencyInfo(readiness.required_proficiency).icon}</span>}
                    label={getProficiencyInfo(readiness.required_proficiency).label}
                    sx={{
                      bgcolor: getProficiencyInfo(readiness.required_proficiency).color,
                      color: 'white',
                      fontWeight: 'bold'
                    }}
                  />
                </Box>
              )}

              {/* Estimated Study Time */}
              {readiness.estimated_study_hours && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Recommended Study Time
                  </Typography>
                  <Typography variant="h5" color="primary.main" fontWeight="bold">
                    {readiness.estimated_study_hours} hours
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Missing Skills */}
      {missingSkills.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <WarningIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'warning.main' }} />
              Skills Requiring Attention ({missingSkills.length})
            </Typography>

            <List>
              {missingSkills.map((skill, index) => (
                <div key={index}>
                  <ListItem>
                    <ListItemIcon>
                      <IncompleteIcon color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary={skill.skill_name}
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            Current: {(skill.current_score * 100).toFixed(0)}% | 
                            Required: {(skill.required_score * 100).toFixed(0)}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={skill.current_score * 100}
                            sx={{
                              mt: 1,
                              height: 6,
                              borderRadius: 1,
                              bgcolor: 'grey.200',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: skill.current_score >= skill.required_score ? 'success.main' : 'error.main'
                              }
                            }}
                          />
                        </Box>
                      }
                    />
                    <Chip
                      label={`${((skill.required_score - skill.current_score) * 100).toFixed(0)}% gap`}
                      size="small"
                      color="error"
                      variant="outlined"
                    />
                  </ListItem>
                  {index < missingSkills.length - 1 && <Divider />}
                </div>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Strengths */}
      {strengthSkills.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <TrophyIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'success.main' }} />
              Your Strengths ({strengthSkills.length})
            </Typography>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {strengthSkills.map((skill, index) => (
                <Chip
                  key={index}
                  icon={<CompletedIcon />}
                  label={`${skill.skill_name} (${(skill.score * 100).toFixed(0)}%)`}
                  color="success"
                  variant="outlined"
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Recommended Actions */}
      {recommendedActions.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <TipIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'info.main' }} />
              Recommended Study Plan
            </Typography>

            <Stepper orientation="vertical">
              {recommendedActions.map((action, index) => (
                <Step key={index} active>
                  <StepLabel
                    StepIconComponent={() => (
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          bgcolor: 'primary.main',
                          color: 'white',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold'
                        }}
                      >
                        {index + 1}
                      </Box>
                    )}
                  >
                    <Typography variant="subtitle1" fontWeight="bold">
                      {action.action}
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {action.description}
                    </Typography>
                    {action.estimated_time && (
                      <Chip
                        label={`${action.estimated_time} hours`}
                        size="small"
                        color="info"
                        variant="outlined"
                      />
                    )}
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>
      )}

      {/* Practice Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <ProgressIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'primary.main' }} />
              Recommended Practice Tests
            </Typography>

            {recommendations.slice(0, 3).map((rec, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {rec.title}
                    </Typography>
                    <Chip
                      label={rec.assessment_type}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {rec.reason}
                  </Typography>
                  
                  {rec.target_skills && rec.target_skills.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        Target Skills:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {rec.target_skills.map((skill, skillIndex) => (
                          <Chip key={skillIndex} label={skill} size="small" />
                        ))}
                      </Box>
                    </Box>
                  )}

                  <Button
                    variant="contained"
                    startIcon={<StartIcon />}
                    size="small"
                  >
                    Start Practice Test
                  </Button>
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Action Button */}
      {isReady && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            color="success"
            startIcon={<TrophyIcon />}
            sx={{ px: 6, py: 2 }}
          >
            Take Certification Exam
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default CertificationPrepDashboard;
