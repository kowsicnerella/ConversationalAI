import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Button,
  Chip,
  Paper,
  Tabs,
  Tab,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fade,
  useTheme,
  useMediaQuery,
  Stack,
  alpha,
} from "@mui/material";
import {
  Quiz,
  School,
  ChromeReaderMode,
  Create,
  RecordVoiceOver,
  PlayArrow,
  Star,
  Timer,
  TrendingUp,
  Close,
  Style,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";

// Import activity components
import QuizActivity from "../../components/activities/QuizActivity";
import FlashcardActivity from "../../components/activities/FlashcardActivity";
import ReadingComprehensionActivity from "../../components/activities/ReadingComprehensionActivity";
import WritingPromptActivity from "../../components/activities/WritingPromptActivity";
import RolePlayActivity from "../../components/activities/RolePlayActivity";

const activityTypes = [
  {
    id: "quiz",
    title: "Interactive Quiz",
    description:
      "Test your knowledge with animated quizzes and instant feedback",
    icon: Quiz,
    color: "#2196f3",
    component: QuizActivity,
  },
  {
    id: "flashcards",
    title: "Smart Flashcards",
    description:
      "Learn vocabulary with swipeable flashcards and spaced repetition",
    icon: Style,
    color: "#9c27b0",
    component: FlashcardActivity,
  },
  {
    id: "reading",
    title: "Reading Comprehension",
    description: "Improve reading skills with interactive text highlighting",
    icon: ChromeReaderMode,
    color: "#4caf50",
    component: ReadingComprehensionActivity,
  },
  {
    id: "writing",
    title: "Writing Prompts",
    description:
      "Practice writing with real-time grammar analysis and feedback",
    icon: Create,
    color: "#ff9800",
    component: WritingPromptActivity,
  },
  {
    id: "roleplay",
    title: "Role-Play Scenarios",
    description: "Practice conversations with AI-powered dialogue simulation",
    icon: RecordVoiceOver,
    color: "#f44336",
    component: RolePlayActivity,
  },
];

const mockActivities = {
  quiz: {
    title: "Telugu Grammar Basics",
    timeLimit: 300,
    questions: [
      {
        question:
          'Which of the following is the correct way to say "Hello" in Telugu?',
        options: ["Namaste", "Vanakkam", "Namaskar", "Adaab"],
        correctAnswer: "Namaste",
        explanation:
          "Namaste is the most common greeting in Telugu, used throughout the day.",
        hint: "Think about the most universal greeting across Indian languages.",
        points: 10,
      },
      {
        question: 'What is the Telugu word for "water"?',
        options: ["Neeru", "Pani", "Jal", "Thanni"],
        correctAnswer: "Neeru",
        explanation: "Neeru (నీరు) is the Telugu word for water.",
        points: 10,
      },
      {
        question: 'How do you say "Thank you" in Telugu?',
        options: ["Dhanyawadamulu", "Krupa", "Santosham", "Abhiprayam"],
        correctAnswer: "Dhanyawadamulu",
        explanation:
          "Dhanyawadamulu (ధన్యవాదములు) is the formal way to say thank you in Telugu.",
        points: 10,
      },
    ],
  },
  flashcards: [
    {
      id: 1,
      front: "Hello",
      back: "నమస్తే (Namaste)",
      frontLanguage: "en",
      backLanguage: "te",
      example: "నమస్తే, మీరు ఎలా ఉన్నారు?",
    },
    {
      id: 2,
      front: "Water",
      back: "నీరు (Neeru)",
      frontLanguage: "en",
      backLanguage: "te",
      example: "దయచేసి నీరు ఇవ్వండి",
    },
    {
      id: 3,
      front: "Food",
      back: "ఆహారం (Aaharam)",
      frontLanguage: "en",
      backLanguage: "te",
      example: "ఆహారం చాలా రుచిగా ఉంది",
    },
  ],
  reading: {
    title: "Telugu Culture and Traditions",
    passage:
      "Telugu culture is rich and diverse, with a history spanning over a thousand years. The language itself is one of the classical languages of India, known for its sweetness and melodious sound. Traditional Telugu festivals like Ugadi, Dussehra, and Sankranti are celebrated with great enthusiasm across Andhra Pradesh and Telangana. The cuisine is famous for its spicy and flavorful dishes, including biryani, pulihora, and various types of pickles.",
    translation:
      "తెలుగు సంస్కృతి సమృద్ధమైనది మరియు వైవిధ్యమైనది, వేయి సంవత్సరాలకు మించిన చరిత్రను కలిగి ఉంది...",
    timeLimit: 600,
    questions: [
      {
        question:
          "According to the passage, Telugu is known for what qualities?",
        options: [
          "Complexity and difficulty",
          "Sweetness and melodious sound",
          "Ancient scripts",
          "Regional dialects",
        ],
        correctAnswer: "Sweetness and melodious sound",
        hint: "Look for descriptive words about the language itself.",
      },
      {
        question: "Which festivals are mentioned in the passage?",
        options: [
          "Diwali, Holi, Eid",
          "Ugadi, Dussehra, Sankranti",
          "Christmas, Easter, New Year",
          "Onam, Pongal, Baisakhi",
        ],
        correctAnswer: "Ugadi, Dussehra, Sankranti",
        hint: "Focus on the specific Telugu festivals listed.",
      },
    ],
  },
  writing: {
    title: "Describe Your Hometown",
    prompt:
      "Write a descriptive essay about your hometown. Include details about the people, culture, food, and what makes it special to you. Try to paint a vivid picture for someone who has never been there.",
    context:
      "This writing exercise helps you practice descriptive writing while sharing personal experiences.",
    timeLimit: 1800,
    targetWordCount: 200,
    minWordCount: 100,
    hints: [
      "Use sensory details",
      "Include specific examples",
      "Show, don't tell",
      "Use varied sentence structures",
    ],
    rubric: [
      {
        category: "Content",
        description: "Clear, relevant, and engaging description",
      },
      { category: "Organization", description: "Logical flow and structure" },
      {
        category: "Language",
        description: "Appropriate vocabulary and grammar",
      },
      {
        category: "Creativity",
        description: "Original and interesting perspective",
      },
    ],
  },
  roleplay: {
    title: "At a Telugu Restaurant",
    description:
      "Practice ordering food at a traditional Telugu restaurant. You are a customer, and the AI will play the role of a waiter.",
    timeLimit: 1200,
    steps: [
      {
        type: "ai",
        content:
          "నమస్తే! మా రెస్టారెంట్‌కు స్వాగతం. మీరు ఏమి తీసుకోవాలని అనుకుంటున్నారు?",
        emotion: "professional",
      },
      {
        type: "user",
        hint: "Greet the waiter and ask for the menu",
        placeholder: "Respond politely and ask about the menu...",
        expectedResponse: "Hello, could I see the menu please?",
        keywords: ["hello", "menu", "please"],
        expectedLength: "1-2 sentences",
      },
      {
        type: "ai",
        content:
          "ఇదిగో మెను. మాకు అన్ని రకాల వంటకాలు ఉన్నాయి - బిర్యానీ, పులిహోర, సాంబార్, రసం. మీరు ఏమి ఇష్టపడతారు?",
        emotion: "friendly",
      },
      {
        type: "user",
        hint: "Order your favorite Telugu dish",
        placeholder: "Order something from the menu...",
        expectedResponse: "I would like biryani please",
        keywords: ["biryani", "please", "like"],
        expectedLength: "1-2 sentences",
      },
    ],
    generalHints: [
      'Be polite and use "please" and "thank you"',
      "Ask questions if you need clarification",
      "Show interest in the food and culture",
    ],
    commonPhrases: [
      { english: "Hello", telugu: "నమస్తే (Namaste)" },
      { english: "Please", telugu: "దయచేసి (Dayachesi)" },
      { english: "Thank you", telugu: "ధన్యవాదములు (Dhanyavadamulu)" },
      { english: "I would like", telugu: "నాకు కావాలి (Naaku kaavali)" },
    ],
  },
};

const Activities = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const { activityType } = useParams();
  const [selectedTab, setSelectedTab] = useState(0);
  const [currentActivity, setCurrentActivity] = useState(null);
  const [showActivityDialog, setShowActivityDialog] = useState(false);
  const [activityResults, setActivityResults] = useState(null);

  useEffect(() => {
    if (activityType) {
      const activityIndex = activityTypes.findIndex(
        (type) => type.id === activityType
      );
      if (activityIndex !== -1) {
        setSelectedTab(activityIndex);
        handleStartActivity(activityType);
      }
    }
  }, [activityType]);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handleStartActivity = (activityId) => {
    const activity = activityTypes.find((type) => type.id === activityId);
    const data = mockActivities[activityId];

    if (activity && data) {
      setCurrentActivity({
        type: activity,
        data,
        component: activity.component,
      });
      setShowActivityDialog(true);
    } else {
      toast.error("Activity not available yet!");
    }
  };

  const handleActivityComplete = (results) => {
    setActivityResults(results);
    toast.success("Activity completed!");
    console.log("Activity Results:", results);
  };

  const handleCloseActivity = () => {
    setShowActivityDialog(false);
    setCurrentActivity(null);
    setActivityResults(null);
  };

  const ActivityCard = ({ activity, index }) => (
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
          "&:hover": {
            boxShadow: "0 12px 40px rgba(0,0,0,0.15)",
          },
        }}
        onClick={() => handleStartActivity(activity.id)}
      >
        <Box
          sx={{
            height: 200,
            background: `linear-gradient(135deg, ${activity.color}22, ${activity.color}44)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
          }}
        >
          <activity.icon
            sx={{ fontSize: { xs: 56, sm: 64 }, color: activity.color, opacity: 0.8 }}
          />
          <Box
            sx={{
              position: "absolute",
              top: 16,
              right: 16,
              backgroundColor: "rgba(255,255,255,0.9)",
              borderRadius: "50%",
              p: 1,
            }}
          >
            <PlayArrow sx={{ color: activity.color }} />
          </Box>
        </Box>

        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", mb: 1 }}>
            {activity.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {activity.description}
          </Typography>

          <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
            <Chip label="Interactive" size="small" variant="outlined" />
            <Chip label="AI-Powered" size="small" variant="outlined" />
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Timer sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="caption" color="text.secondary">
                15-30 min
              </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Star sx={{ fontSize: 16, color: "#ffc107" }} />
              <Typography variant="caption" color="text.secondary">
                4.8
              </Typography>
            </Box>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 3, pt: 0 }}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={(e) => {
              e.stopPropagation();
              handleStartActivity(activity.id);
            }}
            sx={{
              borderRadius: 2,
              backgroundColor: activity.color,
              "&:hover": {
                backgroundColor: activity.color,
                filter: "brightness(0.9)",
              },
            }}
          >
            Start Activity
          </Button>
        </CardActions>
      </Card>
    </motion.div>
  );

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 2, sm: 3, md: 4 }, px: { xs: 2, sm: 3 } }}>
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
          <School sx={{ fontSize: { xs: 40, sm: 48 }, mb: 1.5 }} />
          <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: "bold", mb: 1.5 }}>
            Interactive Activities
          </Typography>
          <Typography variant={isMobile ? "body2" : "body1"} sx={{ opacity: 0.9 }}>
            Engage with dynamic learning experiences designed to accelerate your
            progress
          </Typography>
        </Paper>

        {/* Stats Cards */}
        <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }} sx={{ mb: { xs: 3, sm: 4 } }}>
          <Grid item xs={12} sm={4}>
            <motion.div whileHover={{ scale: isMobile ? 1 : 1.02 }}>
              <Paper sx={{ p: { xs: 2, sm: 2.5 }, textAlign: "center", borderRadius: 3 }}>
                <TrendingUp sx={{ fontSize: { xs: 28, sm: 32 }, color: "#4caf50", mb: 1 }} />
                <Typography
                  variant={isMobile ? "h6" : "h5"}
                  sx={{ fontWeight: "bold", color: "#4caf50" }}
                >
                  {activityTypes.length}
                </Typography>
                <Typography variant={isMobile ? "caption" : "body2"} color="text.secondary">
                  Activity Types
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
          <Grid item xs={12} sm={4}>
            <motion.div whileHover={{ scale: isMobile ? 1 : 1.02 }}>
              <Paper sx={{ p: { xs: 2, sm: 2.5 }, textAlign: "center", borderRadius: 3 }}>
                <Quiz sx={{ fontSize: { xs: 28, sm: 32 }, color: "#2196f3", mb: 1 }} />
                <Typography
                  variant={isMobile ? "h6" : "h5"}
                  sx={{ fontWeight: "bold", color: "#2196f3" }}
                >
                  50+
                </Typography>
                <Typography variant={isMobile ? "caption" : "body2"} color="text.secondary">
                  Interactive Exercises
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
          <Grid item xs={12} sm={4}>
            <motion.div whileHover={{ scale: isMobile ? 1 : 1.02 }}>
              <Paper sx={{ p: { xs: 2, sm: 2.5 }, textAlign: "center", borderRadius: 3 }}>
                <Star sx={{ fontSize: { xs: 28, sm: 32 }, color: "#ff9800", mb: 1 }} />
                <Typography
                  variant={isMobile ? "h6" : "h5"}
                  sx={{ fontWeight: "bold", color: "#ff9800" }}
                >
                  4.9
                </Typography>
                <Typography variant={isMobile ? "caption" : "body2"} color="text.secondary">
                  Average Rating
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>

        {/* Activity Categories */}
        <Paper sx={{ borderRadius: 3, overflow: "hidden", mb: { xs: 3, sm: 4 } }}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ borderBottom: 1, borderColor: "divider" }}
          >
            <Tab 
              label="All Activities" 
              sx={{ minHeight: { xs: 56, sm: 72 }, fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            />
            {activityTypes.map((activity) => (
              <Tab
                key={activity.id}
                label={activity.title}
                icon={<activity.icon sx={{ fontSize: { xs: 18, sm: 20 } }} />}
                iconPosition={isMobile ? "start" : "start"}
                sx={{ minHeight: { xs: 56, sm: 72 }, fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
              />
            ))}
          </Tabs>
        </Paper>

        {/* Activities Grid */}
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
              {(selectedTab === 0
                ? activityTypes
                : [activityTypes[selectedTab - 1]]
              ).map((activity, index) => (
                <Grid item xs={12} sm={6} md={4} key={activity.id}>
                  <ActivityCard activity={activity} index={index} />
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </AnimatePresence>
      </motion.div>

      {/* Activity Dialog */}
      <Dialog
        open={showActivityDialog}
        onClose={handleCloseActivity}
        maxWidth="xl"
        fullWidth
        fullScreen
        TransitionComponent={Fade}
        TransitionProps={{ timeout: 500 }}
      >
        <DialogTitle
          sx={{
            p: 2,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: "bold" }}>
            {currentActivity?.type.title}
          </Typography>
          <IconButton onClick={handleCloseActivity} edge="end">
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {currentActivity && (
            <currentActivity.component
              {...(currentActivity.type.id === "quiz"
                ? { quizData: currentActivity.data }
                : currentActivity.type.id === "flashcards"
                ? { flashcards: currentActivity.data }
                : currentActivity.type.id === "reading"
                ? { comprehensionData: currentActivity.data }
                : currentActivity.type.id === "writing"
                ? { promptData: currentActivity.data }
                : currentActivity.type.id === "roleplay"
                ? { scenarioData: currentActivity.data }
                : {})}
              onComplete={handleActivityComplete}
              onNext={() => {
                handleCloseActivity();
                toast.success("Great job! Try another activity.");
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default Activities;
