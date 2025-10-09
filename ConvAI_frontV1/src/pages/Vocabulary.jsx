import { useState, useEffect } from "react";import { useState, useEffect } from "react";

import {import {

  Box,  Box,

  Grid,  Grid,

  Card,  Card,

  CardContent,  CardContent,

  Typography,  Typography,

  TextField,  TextField,

  InputAdornment,  InputAdornment,

  Chip,  Chip,

  Button,  Button,

  IconButton,  IconButton,

  CircularProgress,  Tabs,

  Tooltip,  Tab,

  Dialog,  CircularProgress,

  DialogTitle,  Tooltip,

  DialogContent,  Dialog,

  DialogActions,  DialogTitle,

  MenuItem,  DialogContent,

  Select,  DialogActions,

  FormControl,  MenuItem,

  InputLabel,  Select,

  Alert,  FormControl,

  Snackbar,  InputLabel,

} from "@mui/material";  Alert,

import {  Snackbar,

  Search,} from "@mui/material";

  VolumeUp,import {

  Delete,  Search,

  Edit,  VolumeUp,

  Add,  Delete,

  Star,  Edit,

  StarBorder,  Add,

  PlayArrow,  Star,

} from "@mui/icons-material";  StarBorder,

import { motion, AnimatePresence } from "framer-motion";  PlayArrow,

import PageTransition from "../components/common/PageTransition";  FilterList,

import GradientText from "../components/common/GradientText";} from "@mui/icons-material";

import AnimatedButton from "../components/common/AnimatedButton";import { motion, AnimatePresence } from "framer-motion";

import axiosInstance, { API_ENDPOINTS } from "../config/api";import PageTransition from "../components/common/PageTransition";

import GradientText from "../components/common/GradientText";

const Vocabulary = () => {import AnimatedButton from "../components/common/AnimatedButton";

  const [words, setWords] = useState([]);import axiosInstance, { API_ENDPOINTS } from "../config/api";

  const [stats, setStats] = useState(null);

  const [loading, setLoading] = useState(true);const Vocabulary = () => {

  const [searchTerm, setSearchTerm] = useState("");  const [words, setWords] = useState([]);

  const [difficultyFilter, setDifficultyFilter] = useState("");  const [stats, setStats] = useState(null);

  const [masteryFilter, setMasteryFilter] = useState("");  const [loading, setLoading] = useState(true);

  const [page, setPage] = useState(1);  const [searchTerm, setSearchTerm] = useState("");

  const [hasMore, setHasMore] = useState(true);  const [difficultyFilter, setDifficultyFilter] = useState("");

    const [masteryFilter, setMasteryFilter] = useState("");

  // Dialogs  const [page, setPage] = useState(1);

  const [addDialogOpen, setAddDialogOpen] = useState(false);  const [hasMore, setHasMore] = useState(true);

  const [editDialogOpen, setEditDialogOpen] = useState(false);  

  const [selectedWord, setSelectedWord] = useState(null);  // Dialogs

    const [addDialogOpen, setAddDialogOpen] = useState(false);

  // Snackbar  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });  const [selectedWord, setSelectedWord] = useState(null);

    

  // Form data  // Snackbar

  const [formData, setFormData] = useState({  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

    english_word: "",  

    telugu_translation: "",  // Form data

    phonetic_spelling: "",  const [formData, setFormData] = useState({

    definition: "",    english_word: "",

    example_sentence: "",    telugu_translation: "",

    difficulty_level: "beginner",    phonetic_spelling: "",

    mastery_level: "learning",    definition: "",

  });    example_sentence: "",

    difficulty_level: "beginner",

  useEffect(() => {    mastery_level: "learning",

    fetchVocabulary();  });

    fetchStats();

  }, [searchTerm, difficultyFilter, masteryFilter, page]);  useEffect(() => {

    fetchVocabulary();

  const fetchVocabulary = async () => {    fetchStats();

    try {  }, [searchTerm, difficultyFilter, masteryFilter, page]);

      setLoading(true);

      const params = {  const fetchVocabulary = async () => {

        page,    try {

        per_page: 20,      setLoading(true);

        search: searchTerm,      const params = {

        difficulty: difficultyFilter,        page,

        mastery_level: masteryFilter,        per_page: 20,

      };        search: searchTerm,

              difficulty: difficultyFilter,

      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.WORDS, { params });        mastery_level: masteryFilter,

      setWords(response.data.words || []);      };

      setHasMore(response.data.pagination?.has_next || false);      

    } catch (error) {      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.WORDS, { params });

      console.error("Error fetching vocabulary:", error);      setWords(response.data.words || []);

      showSnackbar("Failed to load vocabulary", "error");      setHasMore(response.data.pagination?.has_next || false);

    } finally {    } catch (error) {

      setLoading(false);      console.error("Error fetching vocabulary:", error);

    }      showSnackbar("Failed to load vocabulary", "error");

  };    } finally {

      setLoading(false);

  const fetchStats = async () => {    }

    try {  };

      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.STATS);

      setStats(response.data.stats);  const fetchStats = async () => {

    } catch (error) {    try {

      console.error("Error fetching stats:", error);      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.STATS);

    }      setStats(response.data.stats);

  };    } catch (error) {

      console.error("Error fetching stats:", error);

  const handleAddWord = async () => {    }

    try {  };

      await axiosInstance.post(API_ENDPOINTS.VOCABULARY.WORDS, formData);

      showSnackbar("Word added successfully!", "success");  const handleAddWord = async () => {

      setAddDialogOpen(false);    try {

      resetForm();      await axiosInstance.post(API_ENDPOINTS.VOCABULARY.WORDS, formData);

      fetchVocabulary();      showSnackbar("Word added successfully!", "success");

      fetchStats();      setAddDialogOpen(false);

    } catch (error) {      resetForm();

      console.error("Error adding word:", error);      fetchVocabulary();

      showSnackbar(error.response?.data?.error || "Failed to add word", "error");      fetchStats();

    }    } catch (error) {

  };      console.error("Error adding word:", error);

      showSnackbar(error.response?.data?.error || "Failed to add word", "error");

  const handleEditWord = async () => {    }

    try {  };

      await axiosInstance.put(

        API_ENDPOINTS.VOCABULARY.WORDS + `/${selectedWord.id}`,  const handleEditWord = async () => {

        formData    try {

      );      await axiosInstance.put(

      showSnackbar("Word updated successfully!", "success");        API_ENDPOINTS.VOCABULARY.WORDS + `/${selectedWord.id}`,

      setEditDialogOpen(false);        formData

      setSelectedWord(null);      );

      resetForm();      showSnackbar("Word updated successfully!", "success");

      fetchVocabulary();      setEditDialogOpen(false);

    } catch (error) {      setSelectedWord(null);

      console.error("Error updating word:", error);      resetForm();

      showSnackbar("Failed to update word", "error");      fetchVocabulary();

    }    } catch (error) {

  };      console.error("Error updating word:", error);

      showSnackbar("Failed to update word", "error");

  const handleDeleteWord = async (wordId) => {    }

    if (!window.confirm("Are you sure you want to delete this word?")) return;  };

    

    try {  const handleDeleteWord = async (wordId) => {

      await axiosInstance.delete(API_ENDPOINTS.VOCABULARY.WORDS + `/${wordId}`);    if (!window.confirm("Are you sure you want to delete this word?")) return;

      showSnackbar("Word deleted successfully!", "success");    

      fetchVocabulary();    try {

      fetchStats();      await axiosInstance.delete(API_ENDPOINTS.VOCABULARY.WORDS + `/${wordId}`);

    } catch (error) {      showSnackbar("Word deleted successfully!", "success");

      console.error("Error deleting word:", error);      fetchVocabulary();

      showSnackbar("Failed to delete word", "error");      fetchStats();

    }    } catch (error) {

  };      console.error("Error deleting word:", error);

      showSnackbar("Failed to delete word", "error");

  const handleUpdateMastery = async (wordId, newMastery) => {    }

    try {  };

      await axiosInstance.put(API_ENDPOINTS.VOCABULARY.WORDS + `/${wordId}`, {

        mastery_level: newMastery,  const handleUpdateMastery = async (wordId, newMastery) => {

      });    try {

      fetchVocabulary();      await axiosInstance.put(API_ENDPOINTS.VOCABULARY.WORDS + `/${wordId}`, {

      fetchStats();        mastery_level: newMastery,

    } catch (error) {      });

      console.error("Error updating mastery:", error);      fetchVocabulary();

    }      fetchStats();

  };    } catch (error) {

      console.error("Error updating mastery:", error);

  const handlePracticeWords = async () => {    }

    try {  };

      const filters = {

        mastery_level: masteryFilter || undefined,  const handlePracticeWords = async () => {

        difficulty_level: difficultyFilter || undefined,    try {

        review_only: true,      const filters = {

        num_cards: 10,        mastery_level: masteryFilter || undefined,

      };        difficulty_level: difficultyFilter || undefined,

              review_only: true,

      const response = await axiosInstance.post(        num_cards: 10,

        API_ENDPOINTS.VOCABULARY.PRACTICE_FLASHCARDS,      };

        filters      

      );      const response = await axiosInstance.post(

              API_ENDPOINTS.VOCABULARY.PRACTICE_FLASHCARDS,

      showSnackbar(`Generated ${response.data.count} flashcards for practice!`, "success");        filters

    } catch (error) {      );

      console.error("Error generating practice:", error);      

      showSnackbar(error.response?.data?.error || "Failed to generate practice", "error");      // Navigate to flashcard practice with these words

    }      // This would ideally use React Router navigation

  };      showSnackbar(`Generated ${response.data.count} flashcards for practice!`, "success");

    } catch (error) {

  const pronounceWord = (word) => {      console.error("Error generating practice:", error);

    if ("speechSynthesis" in window) {      showSnackbar(error.response?.data?.error || "Failed to generate practice", "error");

      const utterance = new SpeechSynthesisUtterance(word);    }

      utterance.lang = "en-US";  };

      speechSynthesis.speak(utterance);

    }  const pronounceWord = (word) => {

  };    if ("speechSynthesis" in window) {

      const utterance = new SpeechSynthesisUtterance(word);

  const openEditDialog = (word) => {      utterance.lang = "en-US";

    setSelectedWord(word);      speechSynthesis.speak(utterance);

    setFormData({    }

      english_word: word.english_word,  };

      telugu_translation: word.telugu_translation,

      phonetic_spelling: word.phonetic_spelling || "",  const openEditDialog = (word) => {

      definition: word.definition || "",    setSelectedWord(word);

      example_sentence: word.example_sentence || "",    setFormData({

      difficulty_level: word.difficulty_level,      english_word: word.english_word,

      mastery_level: word.mastery_level,      telugu_translation: word.telugu_translation,

    });      phonetic_spelling: word.phonetic_spelling || "",

    setEditDialogOpen(true);      definition: word.definition || "",

  };      example_sentence: word.example_sentence || "",

      difficulty_level: word.difficulty_level,

  const resetForm = () => {      mastery_level: word.mastery_level,

    setFormData({    });

      english_word: "",    setEditDialogOpen(true);

      telugu_translation: "",  };

      phonetic_spelling: "",

      definition: "",  const resetForm = () => {

      example_sentence: "",    setFormData({

      difficulty_level: "beginner",      english_word: "",

      mastery_level: "learning",      telugu_translation: "",

    });      phonetic_spelling: "",

  };      definition: "",

      example_sentence: "",

  const showSnackbar = (message, severity) => {      difficulty_level: "beginner",

    setSnackbar({ open: true, message, severity });      mastery_level: "learning",

  };    });

  };

  const getMasteryColor = (mastery) => {

    switch (mastery) {  const showSnackbar = (message, severity) => {

      case "learning":    setSnackbar({ open: true, message, severity });

        return "warning";  };

      case "familiar":

        return "info";  const getMasteryColor = (mastery) => {

      case "mastered":    switch (mastery) {

        return "success";      case "learning":

      default:        return "warning";

        return "default";      case "familiar":

    }        return "info";

  };      case "mastered":

        return "success";

  const getMasteryIcon = (mastery) => {      default:

    switch (mastery) {        return "default";

      case "mastered":    }

        return <Star />;  };

      default:

        return <StarBorder />;  const getMasteryIcon = (mastery) => {

    }    switch (mastery) {

  };      case "mastered":

        return <Star />;

  if (loading && words.length === 0) {      default:

    return (        return <StarBorder />;

      <Box    }

        sx={{  };

          display: "flex",

          justifyContent: "center",  if (loading && words.length === 0) {

          alignItems: "center",    return (

          minHeight: 400,      <Box

        }}        sx={{

      >          display: "flex",

        <CircularProgress size={60} />          justifyContent: "center",

      </Box>          alignItems: "center",

    );          minHeight: 400,

  }        }}

      >

  return (        <CircularProgress size={60} />

    <PageTransition>      </Box>

      <Box>    );

        {/* Header */}  }

        <Box sx={{ mb: 4 }}>

          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>  return (

            <Box>    <PageTransition>

              <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>      <Box>

                My Vocabulary        {/* Header */}

              </GradientText>        <Box sx={{ mb: 4 }}>

              <Typography variant="body1" color="text.secondary">          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>

                మీ పదజాలం - Review and practice your learned words            <Box>

              </Typography>              <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>

            </Box>                My Vocabulary

            <AnimatedButton              </GradientText>

              variant="contained"              <Typography variant="body1" color="text.secondary">

              startIcon={<Add />}                మీ పదజాలం - Review and practice your learned words

              onClick={() => setAddDialogOpen(true)}              </Typography>

            >            </Box>

              Add Word            <AnimatedButton

            </AnimatedButton>              variant="contained"

          </Box>              startIcon={<Add />}

        </Box>              onClick={() => setAddDialogOpen(true)}

            >

        {/* Stats Cards */}              Add Word

        {stats && (            </AnimatedButton>

          <Grid container spacing={2} sx={{ mb: 4 }}>          </Box>

            <Grid item xs={6} sm={3}>        </Box>

              <Card sx={{ textAlign: "center", p: 2 }}>

                <Typography variant="h4" color="primary.main" fontWeight={700}>        {/* Stats Cards */}

                  {stats.total_words}        {stats && (

                </Typography>          <Grid container spacing={2} sx={{ mb: 4 }}>

                <Typography variant="body2" color="text.secondary">            <Grid item xs={6} sm={3}>

                  Total Words              <Card sx={{ textAlign: "center", p: 2 }}>

                </Typography>                <Typography variant="h4" color="primary.main" fontWeight={700}>

              </Card>                  {stats.total_words}

            </Grid>                </Typography>

            <Grid item xs={6} sm={3}>                <Typography variant="body2" color="text.secondary">

              <Card sx={{ textAlign: "center", p: 2 }}>                  Total Words

                <Typography variant="h4" color="success.main" fontWeight={700}>                </Typography>

                  {stats.mastery_distribution?.mastered || 0}              </Card>

                </Typography>            </Grid>

                <Typography variant="body2" color="text.secondary">            <Grid item xs={6} sm={3}>

                  Mastered              <Card sx={{ textAlign: "center", p: 2 }}>

                </Typography>                <Typography variant="h4" color="success.main" fontWeight={700}>

              </Card>                  {stats.mastery_distribution?.mastered || 0}

            </Grid>                </Typography>

            <Grid item xs={6} sm={3}>                <Typography variant="body2" color="text.secondary">

              <Card sx={{ textAlign: "center", p: 2 }}>                  Mastered

                <Typography variant="h4" color="info.main" fontWeight={700}>                </Typography>

                  {stats.mastery_distribution?.familiar || 0}              </Card>

                </Typography>            </Grid>

                <Typography variant="body2" color="text.secondary">            <Grid item xs={6} sm={3}>

                  Familiar              <Card sx={{ textAlign: "center", p: 2 }}>

                </Typography>                <Typography variant="h4" color="info.main" fontWeight={700}>

              </Card>                  {stats.mastery_distribution?.familiar || 0}

            </Grid>                </Typography>

            <Grid item xs={6} sm={3}>                <Typography variant="body2" color="text.secondary">

              <Card sx={{ textAlign: "center", p: 2 }}>                  Familiar

                <Typography variant="h4" color="warning.main" fontWeight={700}>                </Typography>

                  {stats.review_needed || 0}              </Card>

                </Typography>            </Grid>

                <Typography variant="body2" color="text.secondary">            <Grid item xs={6} sm={3}>

                  Need Review              <Card sx={{ textAlign: "center", p: 2 }}>

                </Typography>                <Typography variant="h4" color="warning.main" fontWeight={700}>

              </Card>                  {stats.review_needed || 0}

            </Grid>                </Typography>

          </Grid>                <Typography variant="body2" color="text.secondary">

        )}                  Need Review

                </Typography>

        {/* Search and Filters */}              </Card>

        <Box sx={{ mb: 4 }}>            </Grid>

          <Grid container spacing={2} alignItems="center">          </Grid>

            <Grid item xs={12} md={6}>        )}

              <TextField

                fullWidth        {/* Search and Filters */}

                placeholder="Search words or translations..."        <Box sx={{ mb: 4 }}>

                value={searchTerm}          <Grid container spacing={2} alignItems="center">

                onChange={(e) => {            <Grid item xs={12} md={6}>

                  setSearchTerm(e.target.value);              <TextField

                  setPage(1);                fullWidth

                }}                placeholder="Search words or translations..."

                InputProps={{                value={searchTerm}

                  startAdornment: (                onChange={(e) => {

                    <InputAdornment position="start">                  setSearchTerm(e.target.value);

                      <Search />                  setPage(1);

                    </InputAdornment>                }}

                  ),                InputProps={{

                }}                  startAdornment: (

              />                    <InputAdornment position="start">

            </Grid>                      <Search />

            <Grid item xs={6} md={2}>                    </InputAdornment>

              <FormControl fullWidth size="small">                  ),

                <InputLabel>Difficulty</InputLabel>                }}

                <Select              />

                  value={difficultyFilter}            </Grid>

                  label="Difficulty"            <Grid item xs={6} md={2}>

                  onChange={(e) => {              <FormControl fullWidth size="small">

                    setDifficultyFilter(e.target.value);                <InputLabel>Difficulty</InputLabel>

                    setPage(1);                <Select

                  }}                  value={difficultyFilter}

                >                  label="Difficulty"

                  <MenuItem value="">All</MenuItem>                  onChange={(e) => {

                  <MenuItem value="beginner">Beginner</MenuItem>                    setDifficultyFilter(e.target.value);

                  <MenuItem value="intermediate">Intermediate</MenuItem>                    setPage(1);

                  <MenuItem value="advanced">Advanced</MenuItem>                  }}

                </Select>                >

              </FormControl>                  <MenuItem value="">All</MenuItem>

            </Grid>                  <MenuItem value="beginner">Beginner</MenuItem>

            <Grid item xs={6} md={2}>                  <MenuItem value="intermediate">Intermediate</MenuItem>

              <FormControl fullWidth size="small">                  <MenuItem value="advanced">Advanced</MenuItem>

                <InputLabel>Mastery</InputLabel>                </Select>

                <Select              </FormControl>

                  value={masteryFilter}            </Grid>

                  label="Mastery"            <Grid item xs={6} md={2}>

                  onChange={(e) => {              <FormControl fullWidth size="small">

                    setMasteryFilter(e.target.value);                <InputLabel>Mastery</InputLabel>

                    setPage(1);                <Select

                  }}                  value={masteryFilter}

                >                  label="Mastery"

                  <MenuItem value="">All</MenuItem>                  onChange={(e) => {

                  <MenuItem value="learning">Learning</MenuItem>                    setMasteryFilter(e.target.value);

                  <MenuItem value="familiar">Familiar</MenuItem>                    setPage(1);

                  <MenuItem value="mastered">Mastered</MenuItem>                  }}

                </Select>                >

              </FormControl>                  <MenuItem value="">All</MenuItem>

            </Grid>                  <MenuItem value="learning">Learning</MenuItem>

            <Grid item xs={12} md={2}>                  <MenuItem value="familiar">Familiar</MenuItem>

              <AnimatedButton                  <MenuItem value="mastered">Mastered</MenuItem>

                fullWidth                </Select>

                variant="outlined"              </FormControl>

                startIcon={<PlayArrow />}            </Grid>

                onClick={handlePracticeWords}            <Grid item xs={12} md={2}>

              >              <AnimatedButton

                Practice                fullWidth

              </AnimatedButton>                variant="outlined"

            </Grid>                startIcon={<PlayArrow />}

          </Grid>                onClick={handlePracticeWords}

        </Box>              >

                Practice

        {/* Vocabulary Cards */}              </AnimatedButton>

        <Grid container spacing={3}>            </Grid>

          <AnimatePresence>          </Grid>

            {words.map((word, index) => (        </Box>

              <Grid item xs={12} sm={6} md={4} key={word.id}>

                <motion.div        {/* Vocabulary Cards */}

                  initial={{ opacity: 0, y: 20 }}        <Grid container spacing={3}>

                  animate={{ opacity: 1, y: 0 }}          <AnimatePresence>

                  exit={{ opacity: 0, y: -20 }}            {words.map((word, index) => (

                  transition={{ duration: 0.3, delay: index * 0.05 }}              <Grid item xs={12} sm={6} md={4} key={word.id}>

                >                <motion.div

                  <Card                  initial={{ opacity: 0, y: 20 }}

                    sx={{                  animate={{ opacity: 1, y: 0 }}

                      height: "100%",                  exit={{ opacity: 0, y: -20 }}

                      display: "flex",                  transition={{ duration: 0.3, delay: index * 0.05 }}

                      flexDirection: "column",                >

                      position: "relative",                  <Card

                      "&:hover": {                    sx={{

                        boxShadow: 6,                      height: "100%",

                        transform: "translateY(-4px)",                      display: "flex",

                        transition: "all 0.3s ease",                      flexDirection: "column",

                      },                      position: "relative",

                    }}                      "&:hover": {

                  >                        boxShadow: 6,

                    <CardContent sx={{ flexGrow: 1 }}>                        transform: "translateY(-4px)",

                      {/* Header with actions */}                        transition: "all 0.3s ease",

                      <Box                      },

                        sx={{                    }}

                          display: "flex",                  >

                          justifyContent: "space-between",                    <CardContent sx={{ flexGrow: 1 }}>

                          alignItems: "start",                      {/* Header with actions */}

                          mb: 2,                      <Box

                        }}                        sx={{

                      >                          display: "flex",

                        <Chip                          justifyContent: "space-between",

                          label={word.difficulty_level}                          alignItems: "start",

                          size="small"                          mb: 2,

                          color={                        }}

                            word.difficulty_level === "beginner"                      >

                              ? "success"                        <Chip

                              : word.difficulty_level === "intermediate"                          label={word.difficulty_level}

                              ? "warning"                          size="small"

                              : "error"                          color={

                          }                            word.difficulty_level === "beginner"

                        />                              ? "success"

                        <Box>                              : word.difficulty_level === "intermediate"

                          <Tooltip title="Pronounce">                              ? "warning"

                            <IconButton                              : "error"

                              size="small"                          }

                              onClick={() => pronounceWord(word.english_word)}                        />

                            >                        <Box>

                              <VolumeUp />                          <Tooltip title="Pronounce">

                            </IconButton>                            <IconButton

                          </Tooltip>                              size="small"

                          <Tooltip title="Edit">                              onClick={() => pronounceWord(word.english_word)}

                            <IconButton                            >

                              size="small"                              <VolumeUp />

                              onClick={() => openEditDialog(word)}                            </IconButton>

                            >                          </Tooltip>

                              <Edit />                          <Tooltip title="Edit">

                            </IconButton>                            <IconButton

                          </Tooltip>                              size="small"

                          <Tooltip title="Delete">                              onClick={() => openEditDialog(word)}

                            <IconButton                            >

                              size="small"                              <Edit />

                              onClick={() => handleDeleteWord(word.id)}                            </IconButton>

                              color="error"                          </Tooltip>

                            >                          <Tooltip title="Delete">

                              <Delete />                            <IconButton

                            </IconButton>                              size="small"

                          </Tooltip>                              onClick={() => handleDeleteWord(word.id)}

                        </Box>                              color="error"

                      </Box>                            >

                              <Delete />

                      {/* Word */}                            </IconButton>

                      <Typography                          </Tooltip>

                        variant="h5"                        </Box>

                        fontWeight={700}                      </Box>

                        color="primary.main"

                        sx={{ mb: 1 }}                      {/* Word */}

                      >                      <Typography

                        {word.english_word}                        variant="h5"

                      </Typography>                        fontWeight={700}

                        color="primary.main"

                      {/* Translation */}                        sx={{ mb: 1 }}

                      <Typography                      >

                        variant="h6"                        {word.english_word}

                        color="secondary.main"                      </Typography>

                        sx={{ mb: 1 }}

                      >                      {/* Translation */}

                        {word.telugu_translation}                      <Typography

                      </Typography>                        variant="h6"

                        color="secondary.main"

                      {/* Phonetic */}                        sx={{ mb: 1 }}

                      {word.phonetic_spelling && (                      >

                        <Typography                        {word.telugu_translation}

                          variant="body2"                      </Typography>

                          color="text.secondary"

                          sx={{ mb: 2, fontStyle: "italic" }}                      {/* Phonetic */}

                        >                      {word.phonetic_spelling && (

                          /{word.phonetic_spelling}/                        <Typography

                        </Typography>                          variant="body2"

                      )}                          color="text.secondary"

                          sx={{ mb: 2, fontStyle: "italic" }}

                      {/* Definition */}                        >

                      {word.definition && (                          /{word.phonetic_spelling}/

                        <Typography                        </Typography>

                          variant="body2"                      )}

                          color="text.secondary"

                          sx={{ mb: 1 }}                      {/* Definition */}

                        >                      {word.definition && (

                          {word.definition}                        <Typography

                        </Typography>                          variant="body2"

                      )}                          color="text.secondary"

                          sx={{ mb: 1 }}

                      {/* Example */}                        >

                      {word.example_sentence && (                          {word.definition}

                        <Typography                        </Typography>

                          variant="body2"                      )}

                          color="text.secondary"

                          sx={{ fontStyle: "italic", mb: 2 }}                      {/* Example */}

                        >                      {word.example_sentence && (

                          "{word.example_sentence}"                        <Typography

                        </Typography>                          variant="body2"

                      )}                          color="text.secondary"

                          sx={{ fontStyle: "italic", mb: 2 }}

                      {/* Mastery Level */}                        >

                      <Box sx={{ mt: "auto", pt: 2 }}>                          "{word.example_sentence}"

                        <Box                        </Typography>

                          sx={{                      )}

                            display: "flex",

                            justifyContent: "space-between",                      {/* Mastery Level */}

                            alignItems: "center",                      <Box sx={{ mt: "auto", pt: 2 }}>

                          }}                        <Box

                        >                          sx={{

                          <Chip                            display: "flex",

                            icon={getMasteryIcon(word.mastery_level)}                            justifyContent: "space-between",

                            label={word.mastery_level}                            alignItems: "center",

                            size="small"                          }}

                            color={getMasteryColor(word.mastery_level)}                        >

                            onClick={() => {                          <Chip

                              const levels = ["learning", "familiar", "mastered"];                            icon={getMasteryIcon(word.mastery_level)}

                              const currentIndex = levels.indexOf(word.mastery_level);                            label={word.mastery_level}

                              const nextLevel = levels[(currentIndex + 1) % levels.length];                            size="small"

                              handleUpdateMastery(word.id, nextLevel);                            color={getMasteryColor(word.mastery_level)}

                            }}                            onClick={() => {

                            sx={{ cursor: "pointer" }}                              const levels = ["learning", "familiar", "mastered"];

                          />                              const currentIndex = levels.indexOf(word.mastery_level);

                          {word.practice_count > 0 && (                              const nextLevel = levels[(currentIndex + 1) % levels.length];

                            <Typography variant="caption" color="text.secondary">                              handleUpdateMastery(word.id, nextLevel);

                              Practiced {word.practice_count}x                            }}

                            </Typography>                            sx={{ cursor: "pointer" }}

                          )}                          />

                        </Box>                          {word.practice_count > 0 && (

                      </Box>                            <Typography variant="caption" color="text.secondary">

                    </CardContent>                              Practiced {word.practice_count}x

                  </Card>                            </Typography>

                </motion.div>                          )}

              </Grid>                        </Box>

            ))}                      </Box>

          </AnimatePresence>                    </CardContent>

        </Grid>                  </Card>

                </motion.div>

        {/* Empty State */}              </Grid>

        {words.length === 0 && !loading && (            ))}

          <Box sx={{ textAlign: "center", py: 8 }}>          </AnimatePresence>

            <Search sx={{ fontSize: 80, color: "text.disabled", mb: 2 }} />        </Grid>

            <Typography variant="h6" color="text.secondary" gutterBottom>

              No words found        {/* Empty State */}

            </Typography>        {words.length === 0 && !loading && (

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>          <Box sx={{ textAlign: "center", py: 8 }}>

              {searchTerm || difficultyFilter || masteryFilter            <Search sx={{ fontSize: 80, color: "text.disabled", mb: 2 }} />

                ? "Try adjusting your search or filters"            <Typography variant="h6" color="text.secondary" gutterBottom>

                : "Start by adding words from activities or manually"}              No words found

            </Typography>            </Typography>

            <AnimatedButton            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>

              variant="contained"              {searchTerm || difficultyFilter || masteryFilter

              startIcon={<Add />}                ? "Try adjusting your search or filters"

              onClick={() => setAddDialogOpen(true)}                : "Start by adding words from activities or manually"}

            >            </Typography>

              Add Your First Word            <AnimatedButton

            </AnimatedButton>              variant="contained"

          </Box>              startIcon={<Add />}

        )}              onClick={() => setAddDialogOpen(true)}

            >

        {/* Load More */}              Add Your First Word

        {hasMore && words.length > 0 && (            </AnimatedButton>

          <Box sx={{ textAlign: "center", mt: 4 }}>          </Box>

            <Button        )}

              variant="outlined"

              onClick={() => setPage(page + 1)}        {/* Load More */}

              disabled={loading}        {hasMore && words.length > 0 && (

            >          <Box sx={{ textAlign: "center", mt: 4 }}>

              {loading ? <CircularProgress size={24} /> : "Load More"}            <Button

            </Button>              variant="outlined"

          </Box>              onClick={() => setPage(page + 1)}

        )}              disabled={loading}

            >

        {/* Add Word Dialog */}              {loading ? <CircularProgress size={24} /> : "Load More"}

        <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>            </Button>

          <DialogTitle>Add New Word</DialogTitle>          </Box>

          <DialogContent>        )}

            <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>

              <TextField        {/* Add Word Dialog */}

                label="English Word *"        <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>

                value={formData.english_word}          <DialogTitle>Add New Word</DialogTitle>

                onChange={(e) =>          <DialogContent>

                  setFormData({ ...formData, english_word: e.target.value })            <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>

                }              <TextField

                fullWidth                label="English Word *"

              />                value={formData.english_word}

              <TextField                onChange={(e) =>

                label="Telugu Translation *"                  setFormData({ ...formData, english_word: e.target.value })

                value={formData.telugu_translation}                }

                onChange={(e) =>                fullWidth

                  setFormData({ ...formData, telugu_translation: e.target.value })              />

                }              <TextField

                fullWidth                label="Telugu Translation *"

              />                value={formData.telugu_translation}

              <TextField                onChange={(e) =>

                label="Phonetic Spelling"                  setFormData({ ...formData, telugu_translation: e.target.value })

                value={formData.phonetic_spelling}                }

                onChange={(e) =>                fullWidth

                  setFormData({ ...formData, phonetic_spelling: e.target.value })              />

                }              <TextField

                fullWidth                label="Phonetic Spelling"

                placeholder="e.g., hə-ˈlō"                value={formData.phonetic_spelling}

              />                onChange={(e) =>

              <TextField                  setFormData({ ...formData, phonetic_spelling: e.target.value })

                label="Definition"                }

                value={formData.definition}                fullWidth

                onChange={(e) =>                placeholder="e.g., hə-ˈlō"

                  setFormData({ ...formData, definition: e.target.value })              />

                }              <TextField

                fullWidth                label="Definition"

                multiline                value={formData.definition}

                rows={2}                onChange={(e) =>

              />                  setFormData({ ...formData, definition: e.target.value })

              <TextField                }

                label="Example Sentence"                fullWidth

                value={formData.example_sentence}                multiline

                onChange={(e) =>                rows={2}

                  setFormData({ ...formData, example_sentence: e.target.value })              />

                }              <TextField

                fullWidth                label="Example Sentence"

                multiline                value={formData.example_sentence}

                rows={2}                onChange={(e) =>

              />                  setFormData({ ...formData, example_sentence: e.target.value })

              <FormControl fullWidth>                }

                <InputLabel>Difficulty Level</InputLabel>                fullWidth

                <Select                multiline

                  value={formData.difficulty_level}                rows={2}

                  label="Difficulty Level"              />

                  onChange={(e) =>              <FormControl fullWidth>

                    setFormData({ ...formData, difficulty_level: e.target.value })                <InputLabel>Difficulty Level</InputLabel>

                  }                <Select

                >                  value={formData.difficulty_level}

                  <MenuItem value="beginner">Beginner</MenuItem>                  label="Difficulty Level"

                  <MenuItem value="intermediate">Intermediate</MenuItem>                  onChange={(e) =>

                  <MenuItem value="advanced">Advanced</MenuItem>                    setFormData({ ...formData, difficulty_level: e.target.value })

                </Select>                  }

              </FormControl>                >

            </Box>                  <MenuItem value="beginner">Beginner</MenuItem>

          </DialogContent>                  <MenuItem value="intermediate">Intermediate</MenuItem>

          <DialogActions>                  <MenuItem value="advanced">Advanced</MenuItem>

            <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>                </Select>

            <Button              </FormControl>

              variant="contained"            </Box>

              onClick={handleAddWord}          </DialogContent>

              disabled={!formData.english_word || !formData.telugu_translation}          <DialogActions>

            >            <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>

              Add Word            <Button

            </Button>              variant="contained"

          </DialogActions>              onClick={handleAddWord}

        </Dialog>              disabled={!formData.english_word || !formData.telugu_translation}

            >

        {/* Edit Word Dialog */}              Add Word

        <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>            </Button>

          <DialogTitle>Edit Word</DialogTitle>          </DialogActions>

          <DialogContent>        </Dialog>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>

              <TextField        {/* Edit Word Dialog */}

                label="English Word"        <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>

                value={formData.english_word}          <DialogTitle>Edit Word</DialogTitle>

                disabled          <DialogContent>

                fullWidth            <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>

              />              <TextField

              <TextField                label="English Word"

                label="Telugu Translation *"                value={formData.english_word}

                value={formData.telugu_translation}                disabled

                onChange={(e) =>                fullWidth

                  setFormData({ ...formData, telugu_translation: e.target.value })              />

                }              <TextField

                fullWidth                label="Telugu Translation *"

              />                value={formData.telugu_translation}

              <TextField                onChange={(e) =>

                label="Phonetic Spelling"                  setFormData({ ...formData, telugu_translation: e.target.value })

                value={formData.phonetic_spelling}                }

                onChange={(e) =>                fullWidth

                  setFormData({ ...formData, phonetic_spelling: e.target.value })              />

                }              <TextField

                fullWidth                label="Phonetic Spelling"

              />                value={formData.phonetic_spelling}

              <TextField                onChange={(e) =>

                label="Definition"                  setFormData({ ...formData, phonetic_spelling: e.target.value })

                value={formData.definition}                }

                onChange={(e) =>                fullWidth

                  setFormData({ ...formData, definition: e.target.value })              />

                }              <TextField

                fullWidth                label="Definition"

                multiline                value={formData.definition}

                rows={2}                onChange={(e) =>

              />                  setFormData({ ...formData, definition: e.target.value })

              <TextField                }

                label="Example Sentence"                fullWidth

                value={formData.example_sentence}                multiline

                onChange={(e) =>                rows={2}

                  setFormData({ ...formData, example_sentence: e.target.value })              />

                }              <TextField

                fullWidth                label="Example Sentence"

                multiline                value={formData.example_sentence}

                rows={2}                onChange={(e) =>

              />                  setFormData({ ...formData, example_sentence: e.target.value })

              <FormControl fullWidth>                }

                <InputLabel>Difficulty Level</InputLabel>                fullWidth

                <Select                multiline

                  value={formData.difficulty_level}                rows={2}

                  label="Difficulty Level"              />

                  onChange={(e) =>              <FormControl fullWidth>

                    setFormData({ ...formData, difficulty_level: e.target.value })                <InputLabel>Difficulty Level</InputLabel>

                  }                <Select

                >                  value={formData.difficulty_level}

                  <MenuItem value="beginner">Beginner</MenuItem>                  label="Difficulty Level"

                  <MenuItem value="intermediate">Intermediate</MenuItem>                  onChange={(e) =>

                  <MenuItem value="advanced">Advanced</MenuItem>                    setFormData({ ...formData, difficulty_level: e.target.value })

                </Select>                  }

              </FormControl>                >

              <FormControl fullWidth>                  <MenuItem value="beginner">Beginner</MenuItem>

                <InputLabel>Mastery Level</InputLabel>                  <MenuItem value="intermediate">Intermediate</MenuItem>

                <Select                  <MenuItem value="advanced">Advanced</MenuItem>

                  value={formData.mastery_level}                </Select>

                  label="Mastery Level"              </FormControl>

                  onChange={(e) =>              <FormControl fullWidth>

                    setFormData({ ...formData, mastery_level: e.target.value })                <InputLabel>Mastery Level</InputLabel>

                  }                <Select

                >                  value={formData.mastery_level}

                  <MenuItem value="learning">Learning</MenuItem>                  label="Mastery Level"

                  <MenuItem value="familiar">Familiar</MenuItem>                  onChange={(e) =>

                  <MenuItem value="mastered">Mastered</MenuItem>                    setFormData({ ...formData, mastery_level: e.target.value })

                </Select>                  }

              </FormControl>                >

            </Box>                  <MenuItem value="learning">Learning</MenuItem>

          </DialogContent>                  <MenuItem value="familiar">Familiar</MenuItem>

          <DialogActions>                  <MenuItem value="mastered">Mastered</MenuItem>

            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>                </Select>

            <Button variant="contained" onClick={handleEditWord}>              </FormControl>

              Save Changes            </Box>

            </Button>          </DialogContent>

          </DialogActions>          <DialogActions>

        </Dialog>            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>

            <Button variant="contained" onClick={handleEditWord}>

        {/* Snackbar */}              Save Changes

        <Snackbar            </Button>

          open={snackbar.open}          </DialogActions>

          autoHideDuration={4000}        </Dialog>

          onClose={() => setSnackbar({ ...snackbar, open: false })}

          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}        {/* Snackbar */}

        >        <Snackbar

          <Alert          open={snackbar.open}

            onClose={() => setSnackbar({ ...snackbar, open: false })}          autoHideDuration={4000}

            severity={snackbar.severity}          onClose={() => setSnackbar({ ...snackbar, open: false })}

            sx={{ width: "100%" }}          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}

          >        >

            {snackbar.message}          <Alert

          </Alert>            onClose={() => setSnackbar({ ...snackbar, open: false })}

        </Snackbar>            severity={snackbar.severity}

      </Box>            sx={{ width: "100%" }}

    </PageTransition>          >

  );            {snackbar.message}

};          </Alert>

        </Snackbar>

export default Vocabulary;      </Box>

    </PageTransition>
  );
};

export default Vocabulary;

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
