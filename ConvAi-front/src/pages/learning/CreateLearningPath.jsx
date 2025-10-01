import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, useFieldArray } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Paper,
  Divider,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  ArrowBack,
  Add,
  Delete,
  ExpandMore,
  Save,
  Preview,
  School,
  PlayCircleFilled,
  Quiz,
  Assignment,
  Chat,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../../store/index.js";
import { toast } from "react-hot-toast";

const difficultyLevels = ["Beginner", "Intermediate", "Advanced"];
const lessonTypes = [
  { value: "video", label: "Video Lesson", icon: PlayCircleFilled },
  { value: "interactive", label: "Interactive Exercise", icon: Quiz },
  { value: "practice", label: "Practice Session", icon: Chat },
  { value: "assignment", label: "Assignment", icon: Assignment },
];

const schema = yup.object().shape({
  title: yup
    .string()
    .required("Title is required")
    .min(5, "Title must be at least 5 characters"),
  description: yup
    .string()
    .required("Description is required")
    .min(20, "Description must be at least 20 characters"),
  difficulty: yup.string().required("Difficulty level is required"),
  duration: yup.string().required("Duration is required"),
  tags: yup.array().min(1, "At least one tag is required"),
  chapters: yup
    .array()
    .of(
      yup.object().shape({
        title: yup.string().required("Chapter title is required"),
        description: yup.string().required("Chapter description is required"),
        lessons: yup
          .array()
          .of(
            yup.object().shape({
              title: yup.string().required("Lesson title is required"),
              type: yup.string().required("Lesson type is required"),
              duration: yup.string().required("Lesson duration is required"),
            })
          )
          .min(1, "Each chapter must have at least one lesson"),
      })
    )
    .min(1, "At least one chapter is required"),
});

const CreateLearningPath = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [availableTags] = useState([
    "Conversation",
    "Grammar",
    "Vocabulary",
    "Pronunciation",
    "Business",
    "Academic",
    "Travel",
    "Cultural",
    "Beginner",
    "Intermediate",
    "Advanced",
    "Telugu",
    "English",
  ]);

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    setError,
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      title: "",
      description: "",
      difficulty: "",
      duration: "",
      tags: [],
      chapters: [
        {
          title: "",
          description: "",
          lessons: [
            {
              title: "",
              type: "",
              duration: "",
            },
          ],
        },
      ],
    },
  });

  const {
    fields: chapterFields,
    append: appendChapter,
    remove: removeChapter,
  } = useFieldArray({
    control,
    name: "chapters",
  });

  const watchedTags = watch("tags");

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      // API call to create learning path
      const response = await fetch(
        `${
          import.meta.env.VITE_API_URL || "http://localhost:5000"
        }/api/user/learning-paths`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${user?.token}`,
          },
          body: JSON.stringify({
            ...data,
            user_id: user?.id,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create learning path");
      }

      const result = await response.json();
      toast.success("Learning path created successfully!");
      navigate(`/learning-paths/${result.learning_path.id}`);
    } catch (error) {
      toast.error(error.message);
      setError("root", { message: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTagsChange = (event) => {
    setValue("tags", event.target.value);
  };

  const addChapter = () => {
    appendChapter({
      title: "",
      description: "",
      lessons: [
        {
          title: "",
          type: "",
          duration: "",
        },
      ],
    });
  };

  const addLesson = (chapterIndex) => {
    const currentChapters = watch("chapters");
    const updatedChapters = [...currentChapters];
    updatedChapters[chapterIndex].lessons.push({
      title: "",
      type: "",
      duration: "",
    });
    setValue("chapters", updatedChapters);
  };

  const removeLesson = (chapterIndex, lessonIndex) => {
    const currentChapters = watch("chapters");
    const updatedChapters = [...currentChapters];
    updatedChapters[chapterIndex].lessons.splice(lessonIndex, 1);
    setValue("chapters", updatedChapters);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/learning-paths")}
            sx={{ mb: 2 }}
          >
            Back to Learning Paths
          </Button>

          <Paper
            elevation={3}
            sx={{
              p: 4,
              borderRadius: 3,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              textAlign: "center",
            }}
          >
            <School sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
              Create Learning Path
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9 }}>
              Design an engaging learning experience for students
            </Typography>
          </Paper>
        </Box>

        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          {errors.root && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {errors.root.message}
            </Alert>
          )}

          {/* Basic Information */}
          <Card sx={{ mb: 4, borderRadius: 3 }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" sx={{ fontWeight: "bold", mb: 3 }}>
                Basic Information
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    {...register("title")}
                    fullWidth
                    label="Learning Path Title"
                    error={!!errors.title}
                    helperText={errors.title?.message}
                    sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    {...register("description")}
                    fullWidth
                    multiline
                    rows={4}
                    label="Description"
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth error={!!errors.difficulty}>
                    <InputLabel>Difficulty Level</InputLabel>
                    <Select
                      {...register("difficulty")}
                      label="Difficulty Level"
                      sx={{ borderRadius: 2 }}
                    >
                      {difficultyLevels.map((level) => (
                        <MenuItem key={level} value={level}>
                          {level}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    {...register("duration")}
                    fullWidth
                    label="Duration (e.g., 4 weeks)"
                    error={!!errors.duration}
                    helperText={errors.duration?.message}
                    sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth error={!!errors.tags}>
                    <InputLabel>Tags</InputLabel>
                    <Select
                      multiple
                      value={watchedTags}
                      onChange={handleTagsChange}
                      input={<OutlinedInput label="Tags" />}
                      renderValue={(selected) => (
                        <Box
                          sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}
                        >
                          {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                      sx={{ borderRadius: 2 }}
                    >
                      {availableTags.map((tag) => (
                        <MenuItem key={tag} value={tag}>
                          {tag}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Chapters */}
          <Card sx={{ mb: 4, borderRadius: 3 }}>
            <CardContent sx={{ p: 4 }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 3,
                }}
              >
                <Typography variant="h5" sx={{ fontWeight: "bold" }}>
                  Chapters & Lessons
                </Typography>
                <Button
                  startIcon={<Add />}
                  onClick={addChapter}
                  variant="outlined"
                  sx={{ borderRadius: 2 }}
                >
                  Add Chapter
                </Button>
              </Box>

              <AnimatePresence>
                {chapterFields.map((chapter, chapterIndex) => (
                  <motion.div
                    key={chapter.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Accordion
                      defaultExpanded
                      sx={{
                        mb: 2,
                        borderRadius: 2,
                        "&:before": { display: "none" },
                        border: "1px solid",
                        borderColor: "divider",
                      }}
                    >
                      <AccordionSummary
                        expandIcon={<ExpandMore />}
                        sx={{ borderRadius: 2 }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            width: "100%",
                          }}
                        >
                          <Typography variant="h6">
                            Chapter {chapterIndex + 1}
                          </Typography>
                          {chapterFields.length > 1 && (
                            <IconButton
                              onClick={(e) => {
                                e.stopPropagation();
                                removeChapter(chapterIndex);
                              }}
                              size="small"
                              color="error"
                            >
                              <Delete />
                            </IconButton>
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={3}>
                          <Grid item xs={12}>
                            <TextField
                              {...register(`chapters.${chapterIndex}.title`)}
                              fullWidth
                              label="Chapter Title"
                              error={!!errors.chapters?.[chapterIndex]?.title}
                              helperText={
                                errors.chapters?.[chapterIndex]?.title?.message
                              }
                              sx={{
                                "& .MuiOutlinedInput-root": { borderRadius: 2 },
                              }}
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <TextField
                              {...register(
                                `chapters.${chapterIndex}.description`
                              )}
                              fullWidth
                              multiline
                              rows={2}
                              label="Chapter Description"
                              error={
                                !!errors.chapters?.[chapterIndex]?.description
                              }
                              helperText={
                                errors.chapters?.[chapterIndex]?.description
                                  ?.message
                              }
                              sx={{
                                "& .MuiOutlinedInput-root": { borderRadius: 2 },
                              }}
                            />
                          </Grid>
                        </Grid>

                        <Divider sx={{ my: 3 }} />

                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            mb: 2,
                          }}
                        >
                          <Typography variant="h6">Lessons</Typography>
                          <Button
                            startIcon={<Add />}
                            onClick={() => addLesson(chapterIndex)}
                            size="small"
                            variant="outlined"
                          >
                            Add Lesson
                          </Button>
                        </Box>

                        {watch(`chapters.${chapterIndex}.lessons`)?.map(
                          (lesson, lessonIndex) => (
                            <motion.div
                              key={lessonIndex}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: lessonIndex * 0.1 }}
                            >
                              <Paper
                                variant="outlined"
                                sx={{ p: 3, mb: 2, borderRadius: 2 }}
                              >
                                <Box
                                  sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    mb: 2,
                                  }}
                                >
                                  <Typography
                                    variant="subtitle1"
                                    fontWeight="bold"
                                  >
                                    Lesson {lessonIndex + 1}
                                  </Typography>
                                  {watch(`chapters.${chapterIndex}.lessons`)
                                    .length > 1 && (
                                    <IconButton
                                      onClick={() =>
                                        removeLesson(chapterIndex, lessonIndex)
                                      }
                                      size="small"
                                      color="error"
                                    >
                                      <Delete />
                                    </IconButton>
                                  )}
                                </Box>

                                <Grid container spacing={2}>
                                  <Grid item xs={12} md={6}>
                                    <TextField
                                      {...register(
                                        `chapters.${chapterIndex}.lessons.${lessonIndex}.title`
                                      )}
                                      fullWidth
                                      label="Lesson Title"
                                      size="small"
                                      error={
                                        !!errors.chapters?.[chapterIndex]
                                          ?.lessons?.[lessonIndex]?.title
                                      }
                                      helperText={
                                        errors.chapters?.[chapterIndex]
                                          ?.lessons?.[lessonIndex]?.title
                                          ?.message
                                      }
                                    />
                                  </Grid>
                                  <Grid item xs={12} md={3}>
                                    <FormControl fullWidth size="small">
                                      <InputLabel>Type</InputLabel>
                                      <Select
                                        {...register(
                                          `chapters.${chapterIndex}.lessons.${lessonIndex}.type`
                                        )}
                                        label="Type"
                                        error={
                                          !!errors.chapters?.[chapterIndex]
                                            ?.lessons?.[lessonIndex]?.type
                                        }
                                      >
                                        {lessonTypes.map((type) => (
                                          <MenuItem
                                            key={type.value}
                                            value={type.value}
                                          >
                                            <Box
                                              sx={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 1,
                                              }}
                                            >
                                              <type.icon
                                                sx={{ fontSize: 20 }}
                                              />
                                              {type.label}
                                            </Box>
                                          </MenuItem>
                                        ))}
                                      </Select>
                                    </FormControl>
                                  </Grid>
                                  <Grid item xs={12} md={3}>
                                    <TextField
                                      {...register(
                                        `chapters.${chapterIndex}.lessons.${lessonIndex}.duration`
                                      )}
                                      fullWidth
                                      label="Duration"
                                      size="small"
                                      placeholder="e.g., 15 min"
                                      error={
                                        !!errors.chapters?.[chapterIndex]
                                          ?.lessons?.[lessonIndex]?.duration
                                      }
                                      helperText={
                                        errors.chapters?.[chapterIndex]
                                          ?.lessons?.[lessonIndex]?.duration
                                          ?.message
                                      }
                                    />
                                  </Grid>
                                </Grid>
                              </Paper>
                            </motion.div>
                          )
                        )}
                      </AccordionDetails>
                    </Accordion>
                  </motion.div>
                ))}
              </AnimatePresence>
            </CardContent>
          </Card>

          {/* Submit Buttons */}
          <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
            <Button
              variant="outlined"
              startIcon={<Preview />}
              size="large"
              disabled={isLoading}
              sx={{ borderRadius: 2 }}
            >
              Preview
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={<Save />}
              size="large"
              disabled={isLoading}
              sx={{
                borderRadius: 2,
                background: "linear-gradient(135deg, #667eea, #764ba2)",
                px: 4,
              }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "Create Learning Path"
              )}
            </Button>
          </Box>
        </Box>
      </motion.div>
    </Container>
  );
};

export default CreateLearningPath;
