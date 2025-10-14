import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Radio,
  RadioGroup,
  FormControlLabel,
  LinearProgress,
  Chip,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Stack,
  Tabs,
  Tab
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  CheckCircle as CorrectIcon,
  Cancel as WrongIcon,
  EmojiEvents as TrophyIcon,
  AccessTime as TimeIcon,
  Psychology as BrainIcon,
  TrendingUp as ProgressIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import practiceService, {
  calculateSessionStats,
  formatTime,
  getPerformanceLevel,
  getDifficultyInfo,
  getQuestionTypeLabel
} from '../services/practiceService';

const Practice = () => {
  // State for tab selection
  const [activeTab, setActiveTab] = useState(0);

  // State for practice setup
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('beginner');
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionTypes, setQuestionTypes] = useState(['multiple_choice']);
  const [languageFocus, setLanguageFocus] = useState('vocabulary');

  // State for practice session
  const [isActive, setIsActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [answers, setAnswers] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [questionStartTime, setQuestionStartTime] = useState(null);

  // State for results
  const [showResults, setShowResults] = useState(false);
  const [sessionResults, setSessionResults] = useState(null);

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;

  /**
   * Start a new practice session
   */
  const handleStartPractice = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic to practice');
      return;
    }

    setLoading(true);
    try {
      const response = await practiceService.generateQuestions({
        topic,
        difficulty,
        num_questions: numQuestions,
        question_types: questionTypes,
        language_focus: languageFocus
      });

      setQuestions(response.questions || []);
      setCurrentQuestionIndex(0);
      setAnswers([]);
      setIsActive(true);
      setShowResults(false);
      setStartTime(new Date());
      setQuestionStartTime(new Date());
      setShowFeedback(false);
    } catch (error) {
      console.error('Error starting practice:', error);
      alert('Failed to generate questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Submit answer for current question
   */
  const handleSubmitAnswer = async () => {
    if (!userAnswer.trim() && currentQuestion.type !== 'true_false') {
      alert('Please provide an answer');
      return;
    }

    setLoading(true);
    try {
      const timeSpent = questionStartTime 
        ? Math.floor((new Date() - questionStartTime) / 1000)
        : 0;

      const response = await practiceService.submitAnswer({
        question_id: currentQuestion.question_id,
        question_type: currentQuestion.type,
        user_answer: userAnswer,
        correct_answer: currentQuestion.correct_answer,
        question_text: currentQuestion.question,
        options: currentQuestion.options,
        response_time: timeSpent,
        difficulty_level: difficulty
      });

      setLastResult(response);
      setShowFeedback(true);

      // Store answer
      const updatedQuestion = {
        ...currentQuestion,
        user_answer: userAnswer,
        is_correct: response.result.is_correct,
        score: response.result.score,
        feedback: response.feedback,
        telugu_feedback: response.telugu_feedback
      };
      setAnswers([...answers, updatedQuestion]);

    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Move to next question
   */
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setUserAnswer('');
      setShowFeedback(false);
      setLastResult(null);
      setQuestionStartTime(new Date());
    } else {
      // Session complete
      handleCompleteSession();
    }
  };

  /**
   * Complete the practice session
   */
  const handleCompleteSession = () => {
    const stats = calculateSessionStats(answers);
    const totalTime = startTime 
      ? Math.floor((new Date() - startTime) / 1000)
      : 0;

    setSessionResults({
      ...stats,
      totalTime,
      performance: getPerformanceLevel(stats.accuracy)
    });
    setShowResults(true);
    setIsActive(false);
  };

  /**
   * Restart practice with same settings
   */
  const handleRestartPractice = () => {
    handleStartPractice();
  };

  /**
   * Go back to setup
   */
  const handleNewPractice = () => {
    setIsActive(false);
    setShowResults(false);
    setQuestions([]);
    setAnswers([]);
    setCurrentQuestionIndex(0);
    setUserAnswer('');
    setTopic('');
  };

  /**
   * Render practice setup form
   */
  const renderSetupForm = () => (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BrainIcon color="primary" />
          Start a Practice Session
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Choose what you'd like to practice and we'll generate personalized questions
        </Typography>

        <Box sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            {/* Topic */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., greetings, family, numbers, colors"
                helperText="What topic would you like to practice?"
              />
            </Grid>

            {/* Difficulty */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  value={difficulty}
                  label="Difficulty Level"
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <MenuItem value="beginner">🌱 Beginner</MenuItem>
                  <MenuItem value="intermediate">📖 Intermediate</MenuItem>
                  <MenuItem value="advanced">🎓 Advanced</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Number of Questions */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Number of Questions</InputLabel>
                <Select
                  value={numQuestions}
                  label="Number of Questions"
                  onChange={(e) => setNumQuestions(e.target.value)}
                >
                  <MenuItem value={5}>5 Questions (5-10 min)</MenuItem>
                  <MenuItem value={10}>10 Questions (10-20 min)</MenuItem>
                  <MenuItem value={15}>15 Questions (15-30 min)</MenuItem>
                  <MenuItem value={20}>20 Questions (30-40 min)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Language Focus */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Language Focus</InputLabel>
                <Select
                  value={languageFocus}
                  label="Language Focus"
                  onChange={(e) => setLanguageFocus(e.target.value)}
                >
                  <MenuItem value="vocabulary">📝 Vocabulary</MenuItem>
                  <MenuItem value="grammar">📚 Grammar</MenuItem>
                  <MenuItem value="pronunciation">🗣️ Pronunciation</MenuItem>
                  <MenuItem value="mixed">🎯 Mixed</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Question Types */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Question Type</InputLabel>
                <Select
                  value={questionTypes[0]}
                  label="Question Type"
                  onChange={(e) => setQuestionTypes([e.target.value])}
                >
                  <MenuItem value="multiple_choice">✓ Multiple Choice</MenuItem>
                  <MenuItem value="fill_blank">__ Fill in the Blank</MenuItem>
                  <MenuItem value="translation">🔄 Translation</MenuItem>
                  <MenuItem value="true_false">✓✗ True/False</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Start Button */}
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <StartIcon />}
                onClick={handleStartPractice}
                disabled={loading || !topic.trim()}
              >
                {loading ? 'Generating Questions...' : 'Start Practice'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );

  /**
   * Render active practice session
   */
  const renderPracticeSession = () => (
    <Card>
      <CardContent>
        {/* Progress Header */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6">
              Question {currentQuestionIndex + 1} of {questions.length}
            </Typography>
            <Chip
              label={getDifficultyInfo(difficulty).label}
              color={getDifficultyInfo(difficulty).color}
              size="small"
            />
          </Box>
          <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 1 }} />
        </Box>

        {currentQuestion && (
          <>
            {/* Question */}
            <Paper elevation={0} sx={{ p: 3, bgcolor: 'primary.50', mb: 3 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {getQuestionTypeLabel(currentQuestion.type)}
              </Typography>
              <Typography variant="h6" gutterBottom>
                {currentQuestion.question}
              </Typography>
              {currentQuestion.telugu_question && (
                <Typography variant="body2" color="text.secondary">
                  {currentQuestion.telugu_question}
                </Typography>
              )}
            </Paper>

            {/* Answer Input */}
            {!showFeedback && (
              <Box sx={{ mb: 3 }}>
                {currentQuestion.type === 'multiple_choice' && currentQuestion.options && (
                  <RadioGroup value={userAnswer} onChange={(e) => setUserAnswer(e.target.value)}>
                    {currentQuestion.options.map((option, index) => (
                      <FormControlLabel
                        key={index}
                        value={option}
                        control={<Radio />}
                        label={option}
                        sx={{
                          p: 1.5,
                          mb: 1,
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                      />
                    ))}
                  </RadioGroup>
                )}

                {currentQuestion.type === 'fill_blank' && (
                  <TextField
                    fullWidth
                    label="Your Answer"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Type your answer here"
                    multiline
                    rows={2}
                  />
                )}

                {currentQuestion.type === 'translation' && (
                  <TextField
                    fullWidth
                    label="Translation"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Enter your translation"
                    multiline
                    rows={2}
                  />
                )}

                {currentQuestion.type === 'true_false' && (
                  <RadioGroup value={userAnswer} onChange={(e) => setUserAnswer(e.target.value)}>
                    <FormControlLabel value="true" control={<Radio />} label="True" />
                    <FormControlLabel value="false" control={<Radio />} label="False" />
                  </RadioGroup>
                )}

                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleSubmitAnswer}
                  disabled={loading || !userAnswer}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Checking...' : 'Submit Answer'}
                </Button>
              </Box>
            )}

            {/* Feedback */}
            {showFeedback && lastResult && (
              <Box sx={{ mb: 3 }}>
                <Alert
                  severity={lastResult.result.is_correct ? 'success' : 'error'}
                  icon={lastResult.result.is_correct ? <CorrectIcon /> : <WrongIcon />}
                  sx={{ mb: 2 }}
                >
                  <Typography variant="subtitle1" gutterBottom>
                    {lastResult.result.is_correct ? 'Correct!' : 'Not Quite Right'}
                  </Typography>
                  <Typography variant="body2">
                    {lastResult.feedback}
                  </Typography>
                  {lastResult.telugu_feedback && (
                    <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                      {lastResult.telugu_feedback}
                    </Typography>
                  )}
                </Alert>

                {!lastResult.result.is_correct && (
                  <Paper elevation={0} sx={{ p: 2, bgcolor: 'info.50', mb: 2 }}>
                    <Typography variant="subtitle2" color="info.dark">
                      Correct Answer:
                    </Typography>
                    <Typography variant="body1">
                      {currentQuestion.correct_answer}
                    </Typography>
                  </Paper>
                )}

                {lastResult.tip && (
                  <Paper elevation={0} sx={{ p: 2, bgcolor: 'warning.50' }}>
                    <Typography variant="subtitle2" color="warning.dark" gutterBottom>
                      💡 Tip:
                    </Typography>
                    <Typography variant="body2">
                      {lastResult.tip}
                    </Typography>
                  </Paper>
                )}

                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleNextQuestion}
                  sx={{ mt: 2 }}
                >
                  {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'See Results'}
                </Button>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );

  /**
   * Render results screen
   */
  const renderResults = () => (
    <Card>
      <CardContent>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <TrophyIcon sx={{ fontSize: 64, color: sessionResults.performance.color + '.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Practice Complete!
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {sessionResults.performance.message}
          </Typography>
        </Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={6} sm={3}>
            <Paper elevation={0} sx={{ p: 2, textAlign: 'center', bgcolor: 'success.50' }}>
              <Typography variant="h3" color="success.dark">
                {sessionResults.correct}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Correct
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Paper elevation={0} sx={{ p: 2, textAlign: 'center', bgcolor: 'error.50' }}>
              <Typography variant="h3" color="error.dark">
                {sessionResults.incorrect}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Incorrect
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Paper elevation={0} sx={{ p: 2, textAlign: 'center', bgcolor: 'info.50' }}>
              <Typography variant="h3" color="info.dark">
                {sessionResults.accuracy.toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Accuracy
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Paper elevation={0} sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.50' }}>
              <Typography variant="h3" color="warning.dark">
                {formatTime(sessionResults.totalTime)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Time
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Stack spacing={2}>
          <Button
            fullWidth
            variant="contained"
            size="large"
            startIcon={<StartIcon />}
            onClick={handleRestartPractice}
          >
            Practice Same Topic Again
          </Button>
          <Button
            fullWidth
            variant="outlined"
            size="large"
            onClick={handleNewPractice}
          >
            Choose New Topic
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BrainIcon fontSize="large" color="primary" />
          Practice Sessions
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Test your knowledge with AI-generated questions tailored to your level
        </Typography>

        {!isActive && !showResults && renderSetupForm()}
        {isActive && !showResults && renderPracticeSession()}
        {showResults && renderResults()}
      </motion.div>
    </Container>
  );
};

export default Practice;
