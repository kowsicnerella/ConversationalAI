import { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  Button,
  IconButton,
  Tabs,
  Tab,
  CircularProgress,
  Tooltip,
} from "@mui/material";
import {
  Search,
  VolumeUp,
  Bookmark,
  BookmarkBorder,
  Translate,
  Star,
  TrendingUp,
  Check,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const Vocabulary = () => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState(0);
  const [flippedCards, setFlippedCards] = useState(new Set());
  const [bookmarked, setBookmarked] = useState(new Set());
  const [practiced, setPracticed] = useState(new Set());

  useEffect(() => {
    fetchVocabulary();
  }, []);

  const fetchVocabulary = async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.LIST);
      setWords(response.data.words || response.data || []);
    } catch (error) {
      console.error("Error fetching vocabulary:", error);
      // Mock data for demo
      setWords([
        {
          id: 1,
          word: "Hello",
          translation: "హలో",
          pronunciation: "hə-ˈlō",
          partOfSpeech: "Interjection",
          definition: "Used as a greeting or to begin a conversation",
          example: "Hello, how are you today?",
          difficulty: "Beginner",
          category: "Greetings",
        },
        {
          id: 2,
          word: "Beautiful",
          translation: "అందమైన",
          pronunciation: "ˈbyü-tə-fəl",
          partOfSpeech: "Adjective",
          definition: "Pleasing the senses or mind aesthetically",
          example: "The sunset was beautiful.",
          difficulty: "Beginner",
          category: "Adjectives",
        },
        {
          id: 3,
          word: "Accomplish",
          translation: "సాధించు",
          pronunciation: "ə-ˈkäm-plish",
          partOfSpeech: "Verb",
          definition: "To complete successfully; achieve",
          example: "She accomplished all her goals this year.",
          difficulty: "Intermediate",
          category: "Verbs",
        },
        {
          id: 4,
          word: "Knowledge",
          translation: "జ్ఞానం",
          pronunciation: "ˈnä-lij",
          partOfSpeech: "Noun",
          definition:
            "Facts, information, and skills acquired through experience or education",
          example: "Knowledge is power.",
          difficulty: "Intermediate",
          category: "Nouns",
        },
        {
          id: 5,
          word: "Serendipity",
          translation: "అనుకోకుండా కనుగొనడం",
          pronunciation: "ˌser-ən-ˈdi-pə-tē",
          partOfSpeech: "Noun",
          definition:
            "The occurrence of events by chance in a happy or beneficial way",
          example: "Meeting my best friend was pure serendipity.",
          difficulty: "Advanced",
          category: "Abstract",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const toggleFlip = (wordId) => {
    setFlippedCards((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(wordId)) {
        newSet.delete(wordId);
      } else {
        newSet.add(wordId);
      }
      return newSet;
    });
  };

  const toggleBookmark = (wordId) => {
    setBookmarked((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(wordId)) {
        newSet.delete(wordId);
      } else {
        newSet.add(wordId);
      }
      return newSet;
    });
  };

  const markAsPracticed = (wordId) => {
    setPracticed((prev) => new Set(prev).add(wordId));
  };

  const pronounceWord = (word) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(word);
      utterance.lang = "en-US";
      speechSynthesis.speak(utterance);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "Beginner":
        return "success";
      case "Intermediate":
        return "warning";
      case "Advanced":
        return "error";
      default:
        return "default";
    }
  };

  const filteredWords = words.filter((word) => {
    const matchesSearch =
      word.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
      word.translation.includes(searchTerm) ||
      word.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab =
      activeTab === 0
        ? true
        : activeTab === 1
        ? bookmarked.has(word.id)
        : activeTab === 2
        ? practiced.has(word.id)
        : activeTab === 3
        ? word.difficulty === "Beginner"
        : activeTab === 4
        ? word.difficulty === "Intermediate"
        : word.difficulty === "Advanced";
    return matchesSearch && matchesTab;
  });

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <PageTransition>
      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
            Vocabulary Builder
          </GradientText>
          <Typography variant="body1" color="text.secondary">
            Expand your English vocabulary with interactive flashcards
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: "center", p: 2 }}>
              <Typography variant="h4" color="primary.main" fontWeight={700}>
                {words.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Words
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: "center", p: 2 }}>
              <Typography variant="h4" color="success.main" fontWeight={700}>
                {practiced.size}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Practiced
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: "center", p: 2 }}>
              <Typography variant="h4" color="warning.main" fontWeight={700}>
                {bookmarked.size}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Bookmarked
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: "center", p: 2 }}>
              <Typography variant="h4" color="error.main" fontWeight={700}>
                {words.length - practiced.size}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                To Learn
              </Typography>
            </Card>
          </Grid>
        </Grid>

        {/* Search and Filters */}
        <Box sx={{ mb: 4 }}>
          <TextField
            fullWidth
            placeholder="Search words, translations, or categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />

          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="All Words" />
              <Tab label="Bookmarked" />
              <Tab label="Practiced" />
              <Tab label="Beginner" />
              <Tab label="Intermediate" />
              <Tab label="Advanced" />
            </Tabs>
            <AnimatedButton variant="outlined" size="small">
              Start Practice
            </AnimatedButton>
          </Box>
        </Box>

        {/* Vocabulary Cards */}
        <Grid container spacing={3}>
          <AnimatePresence>
            {filteredWords.map((word, index) => {
              const isFlipped = flippedCards.has(word.id);
              return (
                <Grid item xs={12} sm={6} md={4} key={word.id}>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <Card
                      sx={{
                        height: 280,
                        position: "relative",
                        cursor: "pointer",
                        transformStyle: "preserve-3d",
                        transition: "transform 0.6s",
                        transform: isFlipped
                          ? "rotateY(180deg)"
                          : "rotateY(0deg)",
                      }}
                      onClick={() => toggleFlip(word.id)}
                    >
                      {/* Front Side */}
                      <CardContent
                        sx={{
                          position: "absolute",
                          width: "100%",
                          height: "100%",
                          backfaceVisibility: "hidden",
                          display: "flex",
                          flexDirection: "column",
                          justifyContent: "space-between",
                        }}
                      >
                        <Box>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "start",
                              mb: 2,
                            }}
                          >
                            <Chip
                              label={word.difficulty}
                              size="small"
                              color={getDifficultyColor(word.difficulty)}
                            />
                            <Box>
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  pronounceWord(word.word);
                                }}
                              >
                                <VolumeUp />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleBookmark(word.id);
                                }}
                                color={
                                  bookmarked.has(word.id)
                                    ? "primary"
                                    : "default"
                                }
                              >
                                {bookmarked.has(word.id) ? (
                                  <Bookmark />
                                ) : (
                                  <BookmarkBorder />
                                )}
                              </IconButton>
                            </Box>
                          </Box>

                          <Typography
                            variant="h4"
                            fontWeight={700}
                            color="primary.main"
                            sx={{ mb: 1 }}
                          >
                            {word.word}
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mb: 1 }}
                          >
                            /{word.pronunciation}/
                          </Typography>
                          <Chip
                            label={word.partOfSpeech}
                            size="small"
                            variant="outlined"
                          />
                        </Box>

                        <Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <Translate fontSize="small" /> Click to see meaning
                          </Typography>
                        </Box>
                      </CardContent>

                      {/* Back Side */}
                      <CardContent
                        sx={{
                          position: "absolute",
                          width: "100%",
                          height: "100%",
                          backfaceVisibility: "hidden",
                          transform: "rotateY(180deg)",
                          display: "flex",
                          flexDirection: "column",
                          justifyContent: "space-between",
                        }}
                      >
                        <Box>
                          <Typography
                            variant="h5"
                            fontWeight={700}
                            color="secondary.main"
                            sx={{ mb: 2 }}
                          >
                            {word.translation}
                          </Typography>

                          <Typography
                            variant="body2"
                            fontWeight={600}
                            gutterBottom
                          >
                            Definition:
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mb: 2 }}
                          >
                            {word.definition}
                          </Typography>

                          <Typography
                            variant="body2"
                            fontWeight={600}
                            gutterBottom
                          >
                            Example:
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ fontStyle: "italic" }}
                          >
                            "{word.example}"
                          </Typography>
                        </Box>

                        <Box sx={{ display: "flex", gap: 1 }}>
                          {practiced.has(word.id) ? (
                            <Chip
                              icon={<Check />}
                              label="Practiced"
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                          ) : (
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={(e) => {
                                e.stopPropagation();
                                markAsPracticed(word.id);
                              }}
                            >
                              Mark as Practiced
                            </Button>
                          )}
                          <Chip label={word.category} size="small" />
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              );
            })}
          </AnimatePresence>
        </Grid>

        {filteredWords.length === 0 && (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <Search sx={{ fontSize: 80, color: "text.disabled", mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No words found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try adjusting your search or filters
            </Typography>
          </Box>
        )}
      </Box>
    </PageTransition>
  );
};

export default Vocabulary;
