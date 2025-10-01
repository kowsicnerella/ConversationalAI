import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
  Avatar,
  LinearProgress,
  Tooltip,
  Fab,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  useTheme,
  useMediaQuery,
  Stack,
  alpha,
} from "@mui/material";
import {
  Book,
  Search,
  Add,
  VolumeUp,
  Favorite,
  FavoriteBorder,
  School,
  TrendingUp,
  FilterList,
  Sort,
  Star,
  PlayArrow,
  Refresh,
  CheckCircle,
  Cancel,
  Timer,
  Psychology,
  Lightbulb,
  Close,
  MoreVert,
  Edit,
  Delete,
  Share,
  BookmarkAdd,
  Quiz,
  Style,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";
import { vocabularyAPI } from "../services/api";
import { useAuthStore } from "../store";

const vocabularyCategories = [
  {
    id: "basic",
    name: "Basic Words",
    icon: School,
    color: "#4caf50",
    count: 250,
  },
  { id: "daily", name: "Daily Life", icon: Star, color: "#2196f3", count: 180 },
  {
    id: "family",
    name: "Family & Relations",
    icon: Favorite,
    color: "#e91e63",
    count: 95,
  },
  {
    id: "food",
    name: "Food & Drinks",
    icon: Book,
    color: "#ff9800",
    count: 120,
  },
  {
    id: "colors",
    name: "Colors & Shapes",
    icon: Style,
    color: "#9c27b0",
    count: 85,
  },
  {
    id: "numbers",
    name: "Numbers & Time",
    icon: Timer,
    color: "#795548",
    count: 110,
  },
  {
    id: "body",
    name: "Body Parts",
    icon: Psychology,
    color: "#607d8b",
    count: 75,
  },
  {
    id: "nature",
    name: "Nature & Weather",
    icon: Lightbulb,
    color: "#8bc34a",
    count: 140,
  },
];

// Mock data removed - using real API data

const VocabularyPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.down("md"));
  const user = useAuthStore((state) => state.user);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [vocabularyList, setVocabularyList] = useState([]);
  const [selectedWord, setSelectedWord] = useState(null);
  const [showWordDialog, setShowWordDialog] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [sortBy, setSortBy] = useState("alphabetical");
  const [filterBy, setFilterBy] = useState("all");
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showSpacedRepetition, setShowSpacedRepetition] = useState(false);
  const [reviewWords, setReviewWords] = useState([]);
  const [currentReviewIndex, setCurrentReviewIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedWordForMenu, setSelectedWordForMenu] = useState(null);

  // API state
  const [loading, setLoading] = useState(true);
  const [vocabularyStats, setVocabularyStats] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Load vocabulary data from API
  useEffect(() => {
    loadVocabularyData();
    loadVocabularyStats();
  }, [page, sortBy, searchTerm, selectedCategory]);

  useEffect(() => {
    // Calculate words due for review (spaced repetition)
    const now = new Date();
    const wordsForReview = vocabularyList.filter((word) => {
      if (!word.last_practiced) return true;
      const lastPracticed = new Date(word.last_practiced);
      const daysSinceReview = (now - lastPracticed) / (1000 * 60 * 60 * 24);
      const reviewInterval = Math.pow(2, word.practice_count || 0); // Exponential backoff
      return daysSinceReview >= reviewInterval;
    });
    setReviewWords(wordsForReview.slice(0, 10)); // Limit to 10 words per session
  }, [vocabularyList]);

  const loadVocabularyData = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        per_page: 20,
        sort_by: sortBy,
        sort_order: "asc",
      };

      if (searchTerm) params.search = searchTerm;
      if (selectedCategory !== "all") params.difficulty = selectedCategory;

      const response = await vocabularyAPI.getWords(params);

      // Transform API data to match UI expectations
      const transformedWords = response.data.words.map((word) => ({
        id: word.id,
        english: word.english_word,
        telugu: word.telugu_translation,
        pronunciation: word.phonetic_spelling || "",
        category: word.difficulty_level,
        difficulty: word.difficulty_level,
        definition: word.definition || "",
        examples: word.example_sentence
          ? [
              {
                english: word.example_sentence,
                telugu: `Translation: ${word.example_sentence}`,
              },
            ]
          : [],
        mastery:
          word.practice_count > 0
            ? (word.correct_count / word.practice_count) * 100
            : 0,
        lastReviewed: word.last_practiced
          ? new Date(word.last_practiced)
          : null,
        timesReviewed: word.practice_count || 0,
        isFavorite: false, // This could be enhanced with a favorites system
        masteryLevel: word.mastery_level,
      }));

      setVocabularyList(transformedWords);
      setTotalPages(response.data.pagination.pages);
    } catch (error) {
      console.error("Failed to load vocabulary:", error);
      toast.error("Failed to load vocabulary words");
    } finally {
      setLoading(false);
    }
  };

  const loadVocabularyStats = async () => {
    try {
      const response = await vocabularyAPI.getStats();
      setVocabularyStats(response.data.stats);
    } catch (error) {
      console.error("Failed to load vocabulary stats:", error);
    }
  };

  const filteredVocabulary = vocabularyList.filter((word) => {
    const matchesSearch =
      word.english.toLowerCase().includes(searchTerm.toLowerCase()) ||
      word.telugu.includes(searchTerm) ||
      word.pronunciation.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" || word.category === selectedCategory;
    const matchesFilter =
      filterBy === "all" ||
      (filterBy === "favorites" && word.isFavorite) ||
      (filterBy === "mastered" && word.mastery >= 80) ||
      (filterBy === "learning" && word.mastery < 80 && word.mastery > 0) ||
      (filterBy === "new" && word.mastery === 0);

    return matchesSearch && matchesCategory && matchesFilter;
  });

  const sortedVocabulary = [...filteredVocabulary].sort((a, b) => {
    switch (sortBy) {
      case "alphabetical":
        return a.english.localeCompare(b.english);
      case "mastery":
        return b.mastery - a.mastery;
      case "recent":
        return (b.lastReviewed || 0) - (a.lastReviewed || 0);
      case "difficulty":
        return a.difficulty.localeCompare(b.difficulty);
      default:
        return 0;
    }
  });

  const handleWordClick = (word) => {
    setSelectedWord(word);
    setShowWordDialog(true);
  };

  const handlePlayAudio = (audioUrl) => {
    // Simulate audio playback
    toast.success("Playing pronunciation...");
    console.log("Playing audio:", audioUrl);
  };

  const handleToggleFavorite = (wordId) => {
    setVocabularyList((prev) =>
      prev.map((word) =>
        word.id === wordId ? { ...word, isFavorite: !word.isFavorite } : word
      )
    );
    toast.success("Updated favorites!");
  };

  const handleStartSpacedRepetition = () => {
    if (reviewWords.length === 0) {
      toast.error("No words to review right now!");
      return;
    }
    setCurrentReviewIndex(0);
    setShowAnswer(false);
    setShowSpacedRepetition(true);
  };

  const handleReviewAnswer = (correct) => {
    const word = reviewWords[currentReviewIndex];
    const masteryChange = correct ? 10 : -5;
    const newMastery = Math.max(0, Math.min(100, word.mastery + masteryChange));

    setVocabularyList((prev) =>
      prev.map((w) =>
        w.id === word.id
          ? {
              ...w,
              mastery: newMastery,
              lastReviewed: new Date(),
              timesReviewed: w.timesReviewed + 1,
            }
          : w
      )
    );

    if (currentReviewIndex < reviewWords.length - 1) {
      setCurrentReviewIndex(currentReviewIndex + 1);
      setShowAnswer(false);
    } else {
      setShowSpacedRepetition(false);
      toast.success("Review session completed!");
    }
  };

  const handleMenuClick = (event, word) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedWordForMenu(word);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedWordForMenu(null);
  };

  const CategoryCard = ({ category, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -5 }}
    >
      <Card
        sx={{
          height: "100%",
          borderRadius: 3,
          overflow: "hidden",
          cursor: "pointer",
          transition: "all 0.3s ease-in-out",
          border: selectedCategory === category.id ? 2 : 0,
          borderColor: "primary.main",
          "&:hover": {
            boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
          },
        }}
        onClick={() => setSelectedCategory(category.id)}
      >
        <Box
          sx={{
            height: 100,
            background: `linear-gradient(135deg, ${category.color}22, ${category.color}44)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
          }}
        >
          <category.icon
            sx={{ fontSize: 50, color: category.color, opacity: 0.8 }}
          />
          <Chip
            label={category.count}
            size="small"
            sx={{
              position: "absolute",
              top: 8,
              right: 8,
              backgroundColor: category.color,
              color: "white",
              fontWeight: "bold",
            }}
          />
        </Box>
        <CardContent sx={{ p: 2 }}>
          <Typography
            variant="h6"
            sx={{ fontWeight: "bold", textAlign: "center" }}
          >
            {category.name}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );

  const WordCard = ({ word, index }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card
        sx={{
          borderRadius: 2,
          cursor: "pointer",
          transition: "all 0.2s ease-in-out",
          "&:hover": {
            boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
          },
        }}
        onClick={() => handleWordClick(word)}
      >
        <CardContent sx={{ p: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              mb: 1,
            }}
          >
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: "bold", mb: 0.5 }}>
                {word.english}
              </Typography>
              <Typography variant="h6" sx={{ color: "primary.main", mb: 0.5 }}>
                {word.telugu}
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontStyle: "italic" }}
              >
                {word.pronunciation}
              </Typography>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleFavorite(word.id);
                }}
              >
                {word.isFavorite ? (
                  <Favorite color="error" />
                ) : (
                  <FavoriteBorder />
                )}
              </IconButton>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handlePlayAudio(word.audioUrl);
                }}
              >
                <VolumeUp />
              </IconButton>
              <IconButton
                size="small"
                onClick={(e) => handleMenuClick(e, word)}
              >
                <MoreVert />
              </IconButton>
            </Box>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
            <Chip label={word.category} size="small" variant="outlined" />
            <Chip
              label={word.difficulty}
              size="small"
              color={
                word.difficulty === "beginner"
                  ? "success"
                  : word.difficulty === "intermediate"
                  ? "warning"
                  : "error"
              }
            />
          </Box>

          <Box sx={{ mb: 1 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 0.5,
              }}
            >
              <Typography variant="caption" color="text.secondary">
                Mastery: {word.mastery}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Reviewed: {word.timesReviewed}x
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={word.mastery}
              sx={{
                height: 4,
                borderRadius: 2,
                backgroundColor: "grey.200",
                "& .MuiLinearProgress-bar": {
                  backgroundColor:
                    word.mastery >= 80
                      ? "#4caf50"
                      : word.mastery >= 50
                      ? "#ff9800"
                      : "#f44336",
                },
              }}
            />
          </Box>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
            }}
          >
            {word.definition}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );

  CategoryCard.propTypes = {
    category: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
  };

  WordCard.propTypes = {
    word: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
  };

  return (
    <Container
      maxWidth="xl"
      sx={{ py: { xs: 2, sm: 3, md: 4 }, px: { xs: 2, sm: 3 } }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Paper
          elevation={3}
          sx={{
            p: { xs: 3, sm: 4 },
            mb: { xs: 3, sm: 4 },
            borderRadius: 3,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            textAlign: "center",
          }}
        >
          <Book sx={{ fontSize: { xs: 40, sm: 48 }, mb: 1.5 }} />
          <Typography
            variant={isMobile ? "h5" : "h4"}
            sx={{ fontWeight: "bold", mb: 1.5 }}
          >
            Vocabulary Builder
          </Typography>
          <Typography
            variant={isMobile ? "body2" : "body1"}
            sx={{ opacity: 0.9, mb: 2 }}
          >
            Master Telugu vocabulary with smart spaced repetition
          </Typography>

          {/* Stats */}
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={{ xs: 1.5, sm: 3 }}
            justifyContent="center"
            sx={{ mt: 2.5 }}
          >
            <Box sx={{ textAlign: "center" }}>
              <Typography
                variant={isMobile ? "h6" : "h5"}
                sx={{ fontWeight: "bold" }}
              >
                {vocabularyList.length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Total Words
              </Typography>
            </Box>
            <Box sx={{ textAlign: "center" }}>
              <Typography
                variant={isMobile ? "h6" : "h5"}
                sx={{ fontWeight: "bold" }}
              >
                {vocabularyList.filter((w) => w.mastery >= 80).length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Mastered
              </Typography>
            </Box>
            <Box sx={{ textAlign: "center" }}>
              <Typography
                variant={isMobile ? "h6" : "h5"}
                sx={{ fontWeight: "bold" }}
              >
                {reviewWords.length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Due for Review
              </Typography>
            </Box>
          </Stack>
        </Paper>

        {/* Categories */}
        <Box sx={{ mb: { xs: 3, sm: 4 } }}>
          <Typography
            variant={isMobile ? "h6" : "h5"}
            sx={{ fontWeight: "bold", mb: 2 }}
          >
            Categories
          </Typography>
          <Grid container spacing={{ xs: 1.5, sm: 2 }}>
            <Grid item xs={6} sm={4} md={3} lg={2}>
              <Card
                sx={{
                  height: "100%",
                  borderRadius: 3,
                  cursor: "pointer",
                  border: selectedCategory === "all" ? 2 : 0,
                  borderColor: "primary.main",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
                    transform: "translateY(-4px)",
                  },
                }}
                onClick={() => setSelectedCategory("all")}
              >
                <CardContent
                  sx={{ textAlign: "center", py: { xs: 2, sm: 3 }, px: 1 }}
                >
                  <Star
                    sx={{
                      fontSize: { xs: 32, sm: 40 },
                      color: "primary.main",
                      mb: 1,
                    }}
                  />
                  <Typography
                    variant={isMobile ? "body2" : "h6"}
                    sx={{ fontWeight: "bold" }}
                  >
                    All Words
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            {vocabularyCategories.map((category, index) => (
              <Grid item xs={6} sm={4} md={3} lg={2} key={category.id}>
                <CategoryCard category={category} index={index} />
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Controls */}
        <Paper
          sx={{ p: { xs: 2, sm: 3 }, mb: { xs: 2, sm: 3 }, borderRadius: 2 }}
        >
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={{ xs: 2, sm: 2 }}
            flexWrap="wrap"
            alignItems={{ xs: "stretch", sm: "center" }}
          >
            <TextField
              placeholder="Search vocabulary..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size={isMobile ? "small" : "medium"}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{
                flex: { xs: 1, sm: "1 1 250px" },
                minWidth: { xs: "100%", sm: 250 },
              }}
            />

            <FormControl
              size="small"
              sx={{ minWidth: { xs: "100%", sm: 120 } }}
            >
              <InputLabel>Sort by</InputLabel>
              <Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                label="Sort by"
              >
                <MenuItem value="alphabetical">A-Z</MenuItem>
                <MenuItem value="mastery">Mastery</MenuItem>
                <MenuItem value="recent">Recent</MenuItem>
                <MenuItem value="difficulty">Difficulty</MenuItem>
              </Select>
            </FormControl>

            <FormControl
              size="small"
              sx={{ minWidth: { xs: "100%", sm: 120 } }}
            >
              <InputLabel>Filter</InputLabel>
              <Select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value)}
                label="Filter"
              >
                <MenuItem value="all">All Words</MenuItem>
                <MenuItem value="favorites">Favorites</MenuItem>
                <MenuItem value="mastered">Mastered</MenuItem>
                <MenuItem value="learning">Learning</MenuItem>
                <MenuItem value="new">New</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="contained"
              size={isMobile ? "small" : "medium"}
              startIcon={!isMobile && <Refresh />}
              onClick={handleStartSpacedRepetition}
              disabled={reviewWords.length === 0}
              fullWidth={isMobile}
              sx={{ flexShrink: 0 }}
            >
              Review ({reviewWords.length})
            </Button>

            <Button
              variant="outlined"
              size={isMobile ? "small" : "medium"}
              startIcon={!isMobile && <Add />}
              onClick={() => setShowAddDialog(true)}
              fullWidth={isMobile}
              sx={{ flexShrink: 0 }}
            >
              Add Word
            </Button>
          </Stack>
        </Paper>

        {/* Vocabulary List */}
        <Typography
          variant={isMobile ? "h6" : "h5"}
          sx={{ fontWeight: "bold", mb: 2 }}
        >
          {selectedCategory === "all"
            ? "All Vocabulary"
            : vocabularyCategories.find((c) => c.id === selectedCategory)
                ?.name || "Vocabulary"}
          <Chip label={sortedVocabulary.length} size="small" sx={{ ml: 2 }} />
        </Typography>

        {sortedVocabulary.length === 0 ? (
          <Paper sx={{ p: { xs: 3, sm: 4 }, textAlign: "center" }}>
            <Typography
              variant={isMobile ? "subtitle1" : "h6"}
              color="text.secondary"
            >
              No words found matching your criteria
            </Typography>
            <Button
              variant="contained"
              size={isMobile ? "small" : "medium"}
              startIcon={<Add />}
              sx={{ mt: 2 }}
              onClick={() => setShowAddDialog(true)}
            >
              Add Your First Word
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
            {sortedVocabulary.map((word, index) => (
              <Grid item xs={12} sm={6} md={4} key={word.id}>
                <WordCard word={word} index={index} />
              </Grid>
            ))}
          </Grid>
        )}
      </motion.div>

      {/* Word Detail Dialog */}
      <Dialog
        open={showWordDialog}
        onClose={() => setShowWordDialog(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            p: { xs: 2, sm: 3 },
          }}
        >
          <Typography
            variant={isMobile ? "h6" : "h5"}
            sx={{ fontWeight: "bold" }}
          >
            {selectedWord?.english}
          </Typography>
          <IconButton onClick={() => setShowWordDialog(false)}>
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ p: { xs: 2, sm: 3 } }}>
          {selectedWord && (
            <Box>
              <Box sx={{ textAlign: "center", mb: 3 }}>
                <Typography
                  variant={isMobile ? "h5" : "h4"}
                  sx={{ color: "primary.main", mb: 1 }}
                >
                  {selectedWord.telugu}
                </Typography>
                <Typography
                  variant={isMobile ? "body1" : "h6"}
                  sx={{ fontStyle: "italic", color: "text.secondary", mb: 2 }}
                >
                  /{selectedWord.pronunciation}/
                </Typography>
                <Button
                  variant="outlined"
                  size={isMobile ? "small" : "medium"}
                  startIcon={<VolumeUp />}
                  onClick={() => handlePlayAudio(selectedWord.audioUrl)}
                >
                  Play Pronunciation
                </Button>
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                Definition
              </Typography>
              <Typography variant="body1" sx={{ mb: 3 }}>
                {selectedWord.definition}
              </Typography>

              <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                Examples
              </Typography>
              {selectedWord.examples.map((example, index) => (
                <Paper
                  key={index}
                  sx={{ p: 2, mb: 2, backgroundColor: "grey.50" }}
                >
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    <strong>English:</strong> {example.english}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Telugu:</strong> {example.telugu}
                  </Typography>
                </Paper>
              ))}

              {selectedWord.synonyms.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                    Synonyms
                  </Typography>
                  <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    {selectedWord.synonyms.map((synonym, index) => (
                      <Chip key={index} label={synonym} variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}

              <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                <Chip label={selectedWord.category} />
                <Chip label={selectedWord.difficulty} color="primary" />
                <Chip
                  label={`${selectedWord.mastery}% mastered`}
                  color="success"
                />
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>

      {/* Spaced Repetition Dialog */}
      <Dialog
        open={showSpacedRepetition}
        onClose={() => setShowSpacedRepetition(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: "bold" }}>
            Spaced Repetition Review
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {currentReviewIndex + 1} of {reviewWords.length}
          </Typography>
        </DialogTitle>

        <DialogContent>
          {reviewWords[currentReviewIndex] && (
            <Box sx={{ textAlign: "center" }}>
              <LinearProgress
                variant="determinate"
                value={((currentReviewIndex + 1) / reviewWords.length) * 100}
                sx={{ mb: 3, height: 8, borderRadius: 4 }}
              />

              <Typography variant="h4" sx={{ mb: 2 }}>
                {reviewWords[currentReviewIndex].english}
              </Typography>

              {showAnswer ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Typography
                    variant="h4"
                    sx={{ color: "primary.main", mb: 2 }}
                  >
                    {reviewWords[currentReviewIndex].telugu}
                  </Typography>
                  <Typography variant="h6" sx={{ fontStyle: "italic", mb: 3 }}>
                    /{reviewWords[currentReviewIndex].pronunciation}/
                  </Typography>

                  <Box
                    sx={{ display: "flex", gap: 2, justifyContent: "center" }}
                  >
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<Cancel />}
                      onClick={() => handleReviewAnswer(false)}
                    >
                      Incorrect
                    </Button>
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={<CheckCircle />}
                      onClick={() => handleReviewAnswer(true)}
                    >
                      Correct
                    </Button>
                  </Box>
                </motion.div>
              ) : (
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => setShowAnswer(true)}
                >
                  Show Answer
                </Button>
              )}
            </Box>
          )}
        </DialogContent>
      </Dialog>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem
          onClick={() => {
            handleToggleFavorite(selectedWordForMenu?.id);
            handleMenuClose();
          }}
        >
          {selectedWordForMenu?.isFavorite ? <Favorite /> : <FavoriteBorder />}
          <Typography sx={{ ml: 1 }}>
            {selectedWordForMenu?.isFavorite
              ? "Remove from Favorites"
              : "Add to Favorites"}
          </Typography>
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Quiz />
          <Typography sx={{ ml: 1 }}>Practice</Typography>
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Edit />
          <Typography sx={{ ml: 1 }}>Edit</Typography>
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Share />
          <Typography sx={{ ml: 1 }}>Share</Typography>
        </MenuItem>
      </Menu>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{ position: "fixed", bottom: 16, right: 16 }}
        onClick={() => setShowAddDialog(true)}
      >
        <Add />
      </Fab>
    </Container>
  );
};

export default VocabularyPage;
