import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import { ZoomIn, ZoomOut, CenterFocusStrong } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { vocabularyService } from '../../services/vocabularyService';

/**
 * WordNetworkGraph Component
 * Visualizes semantic relationships between vocabulary words
 * Shows synonyms, antonyms, collocations, and derivatives
 */
const WordNetworkGraph = ({ wordId, depth = 2 }) => {
  const [network, setNetwork] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    loadNetwork();
  }, [wordId, depth]);

  const loadNetwork = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await vocabularyService.getWordNetwork(wordId, depth);
      setNetwork(response);
    } catch (err) {
      console.error('Error loading word network:', err);
      setError('Failed to load word network');
    } finally {
      setLoading(false);
    }
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.2, 2));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 0.2, 0.5));
  };

  const handleResetZoom = () => {
    setZoom(1);
  };

  const getRelationshipColor = (type) => {
    const colors = {
      synonym: '#4CAF50',
      antonym: '#F44336',
      collocation: '#2196F3',
      derivative: '#FF9800',
      related: '#9C27B0',
    };
    return colors[type] || '#757575';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!network || !network.central_word) {
    return <Alert severity="info">No network data available for this word.</Alert>;
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Word Network: {network.central_word.word}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Zoom In">
              <IconButton size="small" onClick={handleZoomIn}>
                <ZoomIn />
              </IconButton>
            </Tooltip>
            <Tooltip title="Zoom Out">
              <IconButton size="small" onClick={handleZoomOut}>
                <ZoomOut />
              </IconButton>
            </Tooltip>
            <Tooltip title="Reset Zoom">
              <IconButton size="small" onClick={handleResetZoom}>
                <CenterFocusStrong />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Simple Network Visualization */}
        <Box
          sx={{
            position: 'relative',
            minHeight: 400,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            p: 3,
            transform: `scale(${zoom})`,
            transformOrigin: 'center',
            transition: 'transform 0.3s ease',
          }}
        >
          {/* Central Word */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10,
            }}
          >
            <Chip
              label={network.central_word.word}
              sx={{
                px: 3,
                py: 2,
                fontSize: '1.2rem',
                fontWeight: 700,
                bgcolor: 'primary.main',
                color: 'white',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              }}
              onClick={() => setSelectedNode(network.central_word)}
            />
          </motion.div>

          {/* Related Words by Type */}
          {Object.entries(network.relationships_by_type || {}).map(([type, words], typeIdx) => {
            const angle = (typeIdx / Object.keys(network.relationships_by_type).length) * 2 * Math.PI;
            const radius = 150;

            return words.slice(0, 5).map((word, wordIdx) => {
              const wordAngle = angle + (wordIdx - 2) * 0.3;
              const x = Math.cos(wordAngle) * radius;
              const y = Math.sin(wordAngle) * radius;

              return (
                <motion.div
                  key={`${type}-${wordIdx}`}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.3, delay: typeIdx * 0.1 + wordIdx * 0.05 }}
                  style={{
                    position: 'absolute',
                    top: `calc(50% + ${y}px)`,
                    left: `calc(50% + ${x}px)`,
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  {/* Connection Line */}
                  <svg
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      width: Math.abs(x) + 50,
                      height: Math.abs(y) + 50,
                      transform: 'translate(-50%, -50%)',
                      pointerEvents: 'none',
                      zIndex: 1,
                    }}
                  >
                    <line
                      x1={x > 0 ? 0 : Math.abs(x)}
                      y1={y > 0 ? 0 : Math.abs(y)}
                      x2={x > 0 ? Math.abs(x) : 0}
                      y2={y > 0 ? Math.abs(y) : 0}
                      stroke={getRelationshipColor(type)}
                      strokeWidth="2"
                      strokeOpacity="0.3"
                    />
                  </svg>

                  <Chip
                    label={word.related_word}
                    size="small"
                    sx={{
                      bgcolor: getRelationshipColor(type),
                      color: 'white',
                      fontWeight: 600,
                      cursor: 'pointer',
                      position: 'relative',
                      zIndex: 5,
                      '&:hover': {
                        transform: 'scale(1.1)',
                      },
                      transition: 'transform 0.2s',
                    }}
                    onClick={() => setSelectedNode(word)}
                  />
                </motion.div>
              );
            });
          })}
        </Box>

        {/* Legend */}
        <Box sx={{ mt: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
            Relationship Types:
          </Typography>
          {Object.keys(network.relationships_by_type || {}).map((type) => (
            <Chip
              key={type}
              label={type.charAt(0).toUpperCase() + type.slice(1)}
              size="small"
              sx={{
                bgcolor: getRelationshipColor(type),
                color: 'white',
              }}
            />
          ))}
        </Box>

        {/* Selected Node Info */}
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ mt: 3, p: 2, bgcolor: 'action.hover', borderRadius: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                {selectedNode.related_word || selectedNode.word}
              </Typography>
              {selectedNode.relationship_type && (
                <Chip
                  label={selectedNode.relationship_type}
                  size="small"
                  sx={{
                    bgcolor: getRelationshipColor(selectedNode.relationship_type),
                    color: 'white',
                    mb: 1,
                  }}
                />
              )}
              {selectedNode.strength && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                  Strength: {(selectedNode.strength * 100).toFixed(0)}%
                </Typography>
              )}
            </Box>
          </motion.div>
        )}

        {/* Network Statistics */}
        <Box sx={{ mt: 3, display: 'flex', gap: 3 }}>
          <Box>
            <Typography variant="h6" color="primary.main">
              {network.total_relationships || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total Relationships
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" color="success.main">
              {Object.keys(network.relationships_by_type || {}).length}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Relationship Types
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" color="info.main">
              {network.depth || depth}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Network Depth
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default WordNetworkGraph;
