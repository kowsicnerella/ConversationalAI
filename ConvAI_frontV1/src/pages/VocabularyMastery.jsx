import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Search,
  TrendingUp,
  Schedule,
  LibraryBooks,
  Add,
  FilterList,
  Close,
  PlayArrow,
  Lightbulb,
  ImportContacts,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../components/common/PageTransition';
import GradientText from '../components/common/GradientText';
import VocabularyCard from '../components/vocabulary/VocabularyCard';
import SpacedRepetitionReview from '../components/vocabulary/SpacedRepetitionReview';
import VocabularyStats from '../components/vocabulary/VocabularyStats';
import VocabularyPracticeActivity from '../components/vocabulary/VocabularyPracticeActivity';
import { vocabularyService } from '../services/vocabularyService';

/**
 * VocabularyMastery Page - Phase 5 Implementation
 * Complete SM-2 Spaced Repetition vocabulary learning system
 */
const VocabularyMastery = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [words, setWords] = useState([]);
  const [wordsDue, setWordsDue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  const [filters, setFilters] = useState({
    mastery_level: null,
    difficulty: null,
    topic: null,
    is_favorite: false,
  });
  const [flippedCards, setFlippedCards] = useState(new Set());
  const [showReviewDialog, setShowReviewDialog] = useState(false);
  const [showPracticeDialog, setShowPracticeDialog] = useState(false);
  const [showAddWordDialog, setShowAddWordDialog] = useState(false);
  const [selectedWord, setSelectedWord] = useState(null);
  const [newWord, setNewWord] = useState({ word: '', target_language: 'en' });

  useEffect(() => {
    loadVocabulary();
    loadWordsDue();
  }, [filters]);

  const loadVocabulary = async () => {
    try {
      setLoading(true);
      const response = await vocabularyService.getMyVocabulary({
        ...filters,
        search: searchTerm,
      });
      setWords(response.words || []);
    } catch (error) {
      console.error('Error loading vocabulary:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWordsDue = async () => {
    try {
      const response = await vocabularyService.getWordsDue(5);
      setWordsDue(response.words || []);
    } catch (error) {
      console.error('Error loading words due:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadVocabulary();
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleFlipCard = (wordId) => {
    setFlippedCards((prev) => {
      const next = new Set(prev);
      if (next.has(wordId)) {
        next.delete(wordId);
      } else {
        next.add(wordId);
      }
      return next;
    });
  };

  const handleToggleFavorite = async (wordId) => {
    try {
      await vocabularyService.toggleFavorite(wordId);
      loadVocabulary();
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const handlePracticeWord = (word) => {
    setSelectedWord(word);
    setShowPracticeDialog(true);
  };

  const handleReviewComplete = (results) => {
    setShowReviewDialog(false);
    loadVocabulary();
    loadWordsDue();
  };

  const handlePracticeComplete = (result) => {
    setShowPracticeDialog(false);
    setSelectedWord(null);
    loadVocabulary();
  };

  const handleAddWord = async () => {
    try {
      await vocabularyService.introduceWord(newWord);
      setShowAddWordDialog(false);
      setNewWord({ word: '', target_language: 'en' });
      loadVocabulary();
    } catch (error) {
      console.error('Error adding word:', error);
    }
  };

  const handleFilterClick = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    handleFilterClose();
  };

  const clearFilters = () => {
    setFilters({
      mastery_level: null,
      difficulty: null,
      topic: null,
      is_favorite: false,
    });
  };

  const filteredWords = words.filter((word) =>
    word.word.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeFiltersCount = Object.values(filters).filter((v) => v).length;

  return (
    <PageTransition>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
            <GradientText>Vocabulary Mastery</GradientText>
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Master vocabulary with SM-2 spaced repetition algorithm
          </Typography>
        </Box>

        {/* Quick Actions */}
        {wordsDue.length > 0 && (
          <Alert
            severity="info"
            action={
              <Button
                color="inherit"
                size="small"
                startIcon={<PlayArrow />}
                onClick={() => setShowReviewDialog(true)}
              >
                Start Review
              </Button>
            }
            sx={{ mb: 3 }}
          >
            You have <strong>{wordsDue.length} words</strong> due for review today!
          </Alert>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab icon={<LibraryBooks />} label="My Vocabulary" iconPosition="start" />
            <Tab icon={<Schedule />} label="Review Due" iconPosition="start" />
            <Tab icon={<TrendingUp />} label="Statistics" iconPosition="start" />
          </Tabs>
        </Box>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 0 && (
            <motion.div
              key="my-vocabulary"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Search & Filters */}
              <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  placeholder="Search vocabulary..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch(e)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                  size="small"
                />
                <Button
                  variant="outlined"
                  startIcon={<FilterList />}
                  onClick={handleFilterClick}
                  sx={{ minWidth: 120 }}
                >
                  Filters
                  {activeFiltersCount > 0 && (
                    <Chip
                      label={activeFiltersCount}
                      size="small"
                      color="primary"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Button>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setShowAddWordDialog(true)}
                  sx={{ minWidth: 150 }}
                >
                  Add Word
                </Button>
              </Box>

              {/* Active Filters */}
              {activeFiltersCount > 0 && (
                <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {Object.entries(filters).map(([key, value]) =>
                    value ? (
                      <Chip
                        key={key}
                        label={`${key}: ${value}`}
                        onDelete={() => handleFilterChange(key, null)}
                        size="small"
                      />
                    ) : null
                  )}
                  <Chip label="Clear all" onClick={clearFilters} size="small" variant="outlined" />
                </Box>
              )}

              {/* Vocabulary Grid */}
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                  <Typography>Loading vocabulary...</Typography>
                </Box>
              ) : filteredWords.length === 0 ? (
                <Card>
                  <CardContent sx={{ textAlign: 'center', py: 8 }}>
                    <ImportContacts sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h5" gutterBottom>
                      No Vocabulary Yet
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                      Start building your vocabulary by adding words
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => setShowAddWordDialog(true)}
                    >
                      Add Your First Word
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Grid container spacing={3}>
                  {filteredWords.map((word) => (
                    <Grid item xs={12} sm={6} md={4} key={word.word_id || word.id}>
                      <VocabularyCard
                        word={word}
                        isFlipped={flippedCards.has(word.word_id || word.id)}
                        onFlip={() => handleFlipCard(word.word_id || word.id)}
                        onFavorite={() => handleToggleFavorite(word.word_id || word.id)}
                        onPractice={() => handlePracticeWord(word)}
                        onReview={() => handlePracticeWord(word)}
                        showMasteryInfo={true}
                      />
                    </Grid>
                  ))}
                </Grid>
              )}
            </motion.div>
          )}

          {activeTab === 1 && (
            <motion.div
              key="review-due"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {wordsDue.length > 0 ? (
                <Box>
                  <Alert severity="info" sx={{ mb: 3 }}>
                    <strong>{wordsDue.length} words</strong> are due for review. Regular review helps you retain vocabulary better!
                  </Alert>
                  <Grid container spacing={3}>
                    {wordsDue.map((word) => (
                      <Grid item xs={12} sm={6} md={4} key={word.word_id}>
                        <VocabularyCard
                          word={word}
                          isFlipped={flippedCards.has(word.word_id)}
                          onFlip={() => handleFlipCard(word.word_id)}
                          onFavorite={() => handleToggleFavorite(word.word_id)}
                          onPractice={() => handlePracticeWord(word)}
                          onReview={() => handlePracticeWord(word)}
                          showMasteryInfo={true}
                        />
                      </Grid>
                    ))}
                  </Grid>
                  <Box sx={{ mt: 4, textAlign: 'center' }}>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<PlayArrow />}
                      onClick={() => setShowReviewDialog(true)}
                    >
                      Start Review Session
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Card>
                  <CardContent sx={{ textAlign: 'center', py: 8 }}>
                    <Schedule sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                    <Typography variant="h5" gutterBottom>
                      All Caught Up!
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      No words due for review right now. Great job keeping up with your vocabulary!
                    </Typography>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          )}

          {activeTab === 2 && (
            <motion.div
              key="statistics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <VocabularyStats />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Filter Menu */}
        <Menu anchorEl={filterAnchorEl} open={Boolean(filterAnchorEl)} onClose={handleFilterClose}>
          <MenuItem disabled>
            <Typography variant="subtitle2">Mastery Level</Typography>
          </MenuItem>
          {['new', 'learning', 'familiar', 'mastered'].map((level) => (
            <MenuItem key={level} onClick={() => handleFilterChange('mastery_level', level)}>
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </MenuItem>
          ))}
          <Divider />
          <MenuItem disabled>
            <Typography variant="subtitle2">Difficulty</Typography>
          </MenuItem>
          {['beginner', 'intermediate', 'advanced'].map((diff) => (
            <MenuItem key={diff} onClick={() => handleFilterChange('difficulty', diff)}>
              {diff.charAt(0).toUpperCase() + diff.slice(1)}
            </MenuItem>
          ))}
          <Divider />
          <MenuItem onClick={() => handleFilterChange('is_favorite', !filters.is_favorite)}>
            {filters.is_favorite ? 'Show All' : 'Show Favorites Only'}
          </MenuItem>
        </Menu>

        {/* Review Dialog */}
        <Dialog
          open={showReviewDialog}
          onClose={() => setShowReviewDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Spaced Repetition Review</Typography>
            <IconButton onClick={() => setShowReviewDialog(false)}>
              <Close />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            <SpacedRepetitionReview
              onComplete={handleReviewComplete}
              onClose={() => setShowReviewDialog(false)}
            />
          </DialogContent>
        </Dialog>

        {/* Practice Dialog */}
        <Dialog
          open={showPracticeDialog}
          onClose={() => setShowPracticeDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Practice Activity</Typography>
            <IconButton onClick={() => setShowPracticeDialog(false)}>
              <Close />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            {selectedWord && (
              <VocabularyPracticeActivity
                word={selectedWord}
                onComplete={handlePracticeComplete}
                onClose={() => setShowPracticeDialog(false)}
              />
            )}
          </DialogContent>
        </Dialog>

        {/* Add Word Dialog */}
        <Dialog
          open={showAddWordDialog}
          onClose={() => setShowAddWordDialog(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add New Word</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                label="Word"
                value={newWord.word}
                onChange={(e) => setNewWord({ ...newWord, word: e.target.value })}
                placeholder="Enter a word to learn..."
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Language Code"
                value={newWord.target_language}
                onChange={(e) => setNewWord({ ...newWord, target_language: e.target.value })}
                placeholder="e.g., en, es, fr"
                helperText="Language code of the word"
                sx={{ mb: 3 }}
              />
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button onClick={() => setShowAddWordDialog(false)}>Cancel</Button>
                <Button
                  variant="contained"
                  onClick={handleAddWord}
                  disabled={!newWord.word.trim()}
                >
                  Add Word
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </Dialog>
      </Container>
    </PageTransition>
  );
};

export default VocabularyMastery;
