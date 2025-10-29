/**
 * AssessmentHub Component
 * 
 * Main hub page for all assessment-related functionality:
 * - Browse available assessments
 * - Take assessments
 * - View results and history
 * - Analyze skill diagnostics
 * - Track certification preparation
 * 
 * @component
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Grid,
  Button,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper
} from '@mui/material';
import {
  Search as SearchIcon,
  School as AssessmentIcon,
  Assessment as ResultsIcon,
  Psychology as DiagnosticsIcon,
  EmojiEvents as CertIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

import AssessmentCard from './AssessmentCard';
import AdaptiveTestInterface from './AdaptiveTestInterface';
import ComparisonChart from './ComparisonChart';
import SkillDiagnosticView from './SkillDiagnosticView';
import CertificationPrepDashboard from './CertificationPrepDashboard';

import {
  getAssessments,
  startAssessment,
  getMyHistory,
  getDiagnostics,
  compareAttempts,
  getResults
} from '../../services/assessmentService';

const AssessmentHub = () => {
  // Tab state
  const [currentTab, setCurrentTab] = useState(0);

  // Assessment list state
  const [assessments, setAssessments] = useState([]);
  const [filteredAssessments, setFilteredAssessments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterProficiency, setFilterProficiency] = useState('all');

  // Active assessment state
  const [activeAttemptId, setActiveAttemptId] = useState(null);
  const [takingAssessment, setTakingAssessment] = useState(false);

  // History and results state
  const [history, setHistory] = useState([]);
  const [selectedAttempts, setSelectedAttempts] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [diagnostics, setDiagnostics] = useState([]);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [detailsDialog, setDetailsDialog] = useState(null);

  // Load data on mount
  useEffect(() => {
    loadAssessments();
    loadHistory();
  }, []);

  // Filter assessments
  useEffect(() => {
    filterAssessmentList();
  }, [assessments, searchQuery, filterType, filterProficiency]);

  const loadAssessments = async () => {
    try {
      setLoading(true);
      const response = await getAssessments();
      if (response.success) {
        setAssessments(response.assessments);
      }
    } catch (err) {
      setError(err.message || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await getMyHistory();
      if (response.success) {
        setHistory(response.history);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const filterAssessmentList = () => {
    let filtered = [...assessments];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (assessment) =>
          assessment.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          assessment.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter((assessment) => assessment.assessment_type === filterType);
    }

    // Proficiency filter
    if (filterProficiency !== 'all') {
      filtered = filtered.filter((assessment) => assessment.proficiency_level === filterProficiency);
    }

    setFilteredAssessments(filtered);
  };

  const handleStartAssessment = async (assessment) => {
    try {
      setLoading(true);
      const response = await startAssessment(assessment.id);
      
      if (response.success) {
        setActiveAttemptId(response.attempt.id);
        setTakingAssessment(true);
        setCurrentTab(1); // Switch to "Take Assessment" tab
      }
    } catch (err) {
      setError(err.message || 'Failed to start assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleAssessmentComplete = async (results) => {
    setTakingAssessment(false);
    setActiveAttemptId(null);
    
    // Reload history
    await loadHistory();
    
    // Load diagnostics for the completed attempt
    if (results.attempt_id) {
      try {
        const diagResponse = await getDiagnostics(results.attempt_id);
        if (diagResponse.success) {
          setDiagnostics(diagResponse.diagnostics);
        }
      } catch (err) {
        console.error('Failed to load diagnostics:', err);
      }
    }
    
    // Switch to results tab
    setCurrentTab(2);
  };

  const handleExitAssessment = () => {
    setTakingAssessment(false);
    setActiveAttemptId(null);
    setCurrentTab(0);
  };

  const handleViewDetails = (assessment) => {
    setDetailsDialog(assessment);
  };

  const handleCompareAttempts = async (attemptIds) => {
    if (attemptIds.length !== 2) return;

    try {
      setLoading(true);
      const response = await compareAttempts(attemptIds[0], attemptIds[1]);
      
      if (response.success) {
        setComparisonData(response.comparison);
      }
    } catch (err) {
      setError(err.message || 'Failed to compare attempts');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          <AssessmentIcon sx={{ verticalAlign: 'middle', mr: 2, fontSize: 40 }} />
          Assessment Hub
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Test your skills with adaptive assessments, track your progress, and prepare for certifications.
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={(e, newValue) => setCurrentTab(newValue)}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<AssessmentIcon />} label="Available Tests" />
          <Tab icon={<School />} label="Take Assessment" disabled={!takingAssessment} />
          <Tab icon={<ResultsIcon />} label="My Results" />
          <Tab icon={<DiagnosticsIcon />} label="Skill Diagnostics" />
          <Tab icon={<CertIcon />} label="Certification Prep" />
        </Tabs>
      </Paper>

      {/* Tab 0: Available Assessments */}
      {currentTab === 0 && (
        <Box>
          {/* Filters */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  placeholder="Search assessments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    label="Type"
                  >
                    <MenuItem value="all">All Types</MenuItem>
                    <MenuItem value="placement">Placement</MenuItem>
                    <MenuItem value="progress">Progress</MenuItem>
                    <MenuItem value="mastery">Mastery</MenuItem>
                    <MenuItem value="certification">Certification</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Proficiency</InputLabel>
                  <Select
                    value={filterProficiency}
                    onChange={(e) => setFilterProficiency(e.target.value)}
                    label="Proficiency"
                  >
                    <MenuItem value="all">All Levels</MenuItem>
                    <MenuItem value="beginner">Beginner</MenuItem>
                    <MenuItem value="elementary">Elementary</MenuItem>
                    <MenuItem value="intermediate">Intermediate</MenuItem>
                    <MenuItem value="advanced">Advanced</MenuItem>
                    <MenuItem value="expert">Expert</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>

          {/* Assessment Grid */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : filteredAssessments.length === 0 ? (
            <Alert severity="info">
              No assessments found. Try adjusting your filters.
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {filteredAssessments.map((assessment) => (
                <Grid item xs={12} md={6} lg={4} key={assessment.id}>
                  <AssessmentCard
                    assessment={assessment}
                    onStart={handleStartAssessment}
                    onViewDetails={handleViewDetails}
                  />
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {/* Tab 1: Take Assessment */}
      {currentTab === 1 && takingAssessment && activeAttemptId && (
        <AdaptiveTestInterface
          attemptId={activeAttemptId}
          onComplete={handleAssessmentComplete}
          onExit={handleExitAssessment}
        />
      )}

      {/* Tab 2: My Results */}
      {currentTab === 2 && (
        <Box>
          {history.length === 0 ? (
            <Alert severity="info">
              No assessment history yet. Take an assessment to see your results here.
            </Alert>
          ) : (
            <Box>
              {/* Results Summary */}
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Assessment History ({history.length} attempts)
                </Typography>
                
                {/* Group by assessment */}
                {Object.entries(
                  history.reduce((acc, attempt) => {
                    const key = attempt.assessment_title || 'Unknown';
                    if (!acc[key]) acc[key] = [];
                    acc[key].push(attempt);
                    return acc;
                  }, {})
                ).map(([title, attempts]) => (
                  <Box key={title} sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      {title}
                    </Typography>
                    
                    {attempts.length >= 2 && (
                      <ComparisonChart
                        attempts={attempts}
                        comparisonData={comparisonData}
                      />
                    )}
                  </Box>
                ))}
              </Paper>
            </Box>
          )}
        </Box>
      )}

      {/* Tab 3: Skill Diagnostics */}
      {currentTab === 3 && (
        <Box>
          {diagnostics.length === 0 ? (
            <Alert severity="info">
              No diagnostic data available. Complete an assessment to see your skill analysis.
            </Alert>
          ) : (
            <SkillDiagnosticView diagnostics={diagnostics} />
          )}
        </Box>
      )}

      {/* Tab 4: Certification Prep */}
      {currentTab === 4 && (
        <CertificationPrepDashboard
          userId={null}
          certificationName="General Language Proficiency"
        />
      )}

      {/* Details Dialog */}
      <Dialog
        open={!!detailsDialog}
        onClose={() => setDetailsDialog(null)}
        maxWidth="md"
        fullWidth
      >
        {detailsDialog && (
          <>
            <DialogTitle>
              {detailsDialog.title}
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {detailsDialog.description}
              </Typography>

              {detailsDialog.skill_areas && detailsDialog.skill_areas.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Skill Areas Covered:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {detailsDialog.skill_areas.map((skill, index) => (
                      <Typography key={index} variant="body2">
                        • {skill}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              )}

              {detailsDialog.learning_objectives && detailsDialog.learning_objectives.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Learning Objectives:
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    {detailsDialog.learning_objectives.map((objective, index) => (
                      <Typography key={index} variant="body2" paragraph>
                        {index + 1}. {objective}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsDialog(null)}>Close</Button>
              <Button
                variant="contained"
                onClick={() => {
                  setDetailsDialog(null);
                  handleStartAssessment(detailsDialog);
                }}
              >
                Start Assessment
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default AssessmentHub;
