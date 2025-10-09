import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  IconButton,
  Alert,
  CircularProgress,
  Paper,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel,
  Stack
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Camera as CameraIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  BookmarkBorder as SaveIcon,
  Style as FlashcardIcon,
  Delete as DeleteIcon,
  Image as ImageIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { API_BASE_URL } from '../../config/api';
import { useAuth } from '../../context/AuthContext';

const ImageLearning = () => {
  const { token } = useAuth();
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedObjects, setSelectedObjects] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [flashcardDialogOpen, setFlashcardDialogOpen] = useState(false);
  
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      handleFileSelected(acceptedFiles[0], false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.webp']
    },
    maxSize: 5 * 1024 * 1024, // 5MB
    multiple: false
  });

  const handleFileSelected = (file, isCamera) => {
    setError(null);
    setSuccess(null);
    setAnalysisResult(null);
    setSelectedObjects([]);
    
    // Validate file size
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Only JPG, PNG, and WEBP images are allowed');
      return;
    }
    
    setUploadedImage(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleAnalyzeImage = async () => {
    if (!uploadedImage) return;
    
    setAnalyzing(true);
    setError(null);
    setSuccess(null);
    
    try {
      const formData = new FormData();
      formData.append('image', uploadedImage);
      formData.append('is_camera_capture', 'false');
      formData.append('device_type', 'desktop');
      
      const response = await axios.post(
        `${API_BASE_URL}/image-learning/analyze`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      if (response.data.success) {
        setAnalysisResult(response.data);
        setSuccess(response.data.message);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Image analysis error:', err);
      setError(err.response?.data?.error || 'Failed to analyze image');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectObject = (index) => {
    setSelectedObjects(prev => {
      if (prev.includes(index)) {
        return prev.filter(i => i !== index);
      } else {
        return [...prev, index];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedObjects.length === analysisResult?.objects?.length) {
      setSelectedObjects([]);
    } else {
      setSelectedObjects(analysisResult?.objects.map((_, idx) => idx) || []);
    }
  };

  const handleSaveToVocabulary = async () => {
    if (selectedObjects.length === 0) {
      setError('Please select at least one object to save');
      return;
    }
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/image-learning/${analysisResult.image_id}/save-words`,
        { object_indices: selectedObjects },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data.success) {
        setSuccess(response.data.message);
        setSaveDialogOpen(false);
        setSelectedObjects([]);
      } else {
        setError(response.data.error || 'Failed to save words');
      }
    } catch (err) {
      console.error('Save vocabulary error:', err);
      setError(err.response?.data?.error || 'Failed to save to vocabulary');
    }
  };

  const handleCreateFlashcards = async () => {
    if (selectedObjects.length === 0) {
      setError('Please select at least one object to create flashcards');
      return;
    }
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/image-learning/${analysisResult.image_id}/create-flashcards`,
        { 
          object_indices: selectedObjects,
          difficulty: 'beginner'
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data.success) {
        setSuccess(response.data.message);
        setFlashcardDialogOpen(false);
        setSelectedObjects([]);
      } else {
        setError(response.data.error || 'Failed to create flashcards');
      }
    } catch (err) {
      console.error('Create flashcards error:', err);
      setError(err.response?.data?.error || 'Failed to create flashcards');
    }
  };

  const handleReset = () => {
    setUploadedImage(null);
    setImagePreview(null);
    setAnalysisResult(null);
    setSelectedObjects([]);
    setError(null);
    setSuccess(null);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          📸 Image-Based Learning
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload an image and learn vocabulary from everyday objects
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          చిత్రం ఎక్కించండి మరియు రోజువారీ వస్తువుల నుండి పదకోశాన్ని నేర్చుకోండి
        </Typography>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Upload Section */}
      {!imagePreview && (
        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            mb: 3,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'divider',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.3s',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover'
            }
          }}
        >
          <input {...getInputProps()} />
          <ImageIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop image here' : 'Drag & drop an image, or click to select'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Supported: JPG, PNG, WEBP (max 5MB)
          </Typography>
          
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => fileInputRef.current?.click()}
            >
              Upload from Device
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<CameraIcon />}
              onClick={() => cameraInputRef.current?.click()}
            >
              Take Photo
            </Button>
          </Stack>
          
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onChange={(e) => e.target.files?.[0] && handleFileSelected(e.target.files[0], false)}
          />
          
          <input
            ref={cameraInputRef}
            type="file"
            hidden
            accept="image/*"
            capture="environment"
            onChange={(e) => e.target.files?.[0] && handleFileSelected(e.target.files[0], true)}
          />
        </Paper>
      )}

      {/* Image Preview & Analysis */}
      {imagePreview && (
        <Grid container spacing={3}>
          {/* Uploaded Image */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Uploaded Image</Typography>
                  <IconButton onClick={handleReset} color="error" size="small">
                    <DeleteIcon />
                  </IconButton>
                </Box>
                
                <Box
                  component="img"
                  src={imagePreview}
                  alt="Uploaded"
                  sx={{
                    width: '100%',
                    height: 'auto',
                    maxHeight: 400,
                    objectFit: 'contain',
                    borderRadius: 2,
                    mb: 2
                  }}
                />
                
                {!analysisResult && (
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleAnalyzeImage}
                    disabled={analyzing}
                    startIcon={analyzing ? <CircularProgress size={20} /> : <ImageIcon />}
                  >
                    {analyzing ? 'Analyzing...' : 'Analyze Image'}
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Analysis Results */}
          {analysisResult && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Results
                  </Typography>
                  
                  {analysisResult.scene_description && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        {analysisResult.scene_description}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {analysisResult.scene_description_telugu}
                      </Typography>
                    </Box>
                  )}
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1">
                      Found {analysisResult.total_objects_found} objects
                    </Typography>
                    <Button size="small" onClick={handleSelectAll}>
                      {selectedObjects.length === analysisResult.objects?.length ? 'Deselect All' : 'Select All'}
                    </Button>
                  </Box>
                  
                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={() => setSaveDialogOpen(true)}
                      disabled={selectedObjects.length === 0}
                      size="small"
                    >
                      Save to Vocabulary ({selectedObjects.length})
                    </Button>
                    
                    <Button
                      variant="outlined"
                      startIcon={<FlashcardIcon />}
                      onClick={() => setFlashcardDialogOpen(true)}
                      disabled={selectedObjects.length === 0}
                      size="small"
                    >
                      Create Flashcards
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Identified Objects Grid */}
          {analysisResult?.objects && (
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Identified Objects
              </Typography>
              
              <Grid container spacing={2}>
                {analysisResult.objects.map((obj, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        border: selectedObjects.includes(index) ? 2 : 1,
                        borderColor: selectedObjects.includes(index) ? 'primary.main' : 'divider',
                        transition: 'all 0.3s',
                        '&:hover': {
                          boxShadow: 3
                        }
                      }}
                      onClick={() => handleSelectObject(index)}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Box>
                            <Typography variant="h6" sx={{ fontSize: '1.1rem' }}>
                              {obj.object_name_english}
                            </Typography>
                            <Typography variant="body1" sx={{ color: 'primary.main', fontWeight: 500 }}>
                              {obj.object_name_telugu}
                            </Typography>
                          </Box>
                          
                          <Checkbox
                            checked={selectedObjects.includes(index)}
                            icon={<CheckIcon sx={{ display: 'none' }} />}
                            checkedIcon={<CheckIcon color="primary" />}
                          />
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          🔊 {obj.pronunciation}
                        </Typography>
                        
                        <Divider sx={{ my: 1 }} />
                        
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          {obj.sample_sentence}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          {obj.sentence_telugu}
                        </Typography>
                        
                        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                          <Chip label={obj.category} size="small" />
                          <Chip label={`${(obj.confidence * 100).toFixed(0)}%`} size="small" color="primary" variant="outlined" />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          )}
        </Grid>
      )}

      {/* Save to Vocabulary Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Save to Vocabulary</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Save {selectedObjects.length} selected word{selectedObjects.length !== 1 ? 's' : ''} to your vocabulary?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            These words will be added to your personal vocabulary list for practice.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveToVocabulary} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Flashcards Dialog */}
      <Dialog open={flashcardDialogOpen} onClose={() => setFlashcardDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Flashcards</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Create flashcard session with {selectedObjects.length} selected word{selectedObjects.length !== 1 ? 's' : ''}?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            You can practice these flashcards immediately after creation.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFlashcardDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateFlashcards} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ImageLearning;
