import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Typography,
  Button,
  Box,
  Chip,
  Stack,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Download as DownloadIcon,
  Share as ShareIcon,
  EmojiEvents as TrophyIcon,
  Close as CloseIcon,
  Verified as VerifiedIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import goalsService from '../../services/goalsService';

const CertificateGallery = ({ certificates }) => {
  const [selectedCertificate, setSelectedCertificate] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  const handleCertificateClick = (certificate) => {
    setSelectedCertificate(certificate);
    setDetailDialogOpen(true);
  };

  const handleDownload = async (certificateId) => {
    try {
      await goalsService.downloadCertificate(certificateId);
    } catch (err) {
      console.error('Error downloading certificate:', err);
    }
  };

  const handleShare = () => {
    if (navigator.share && selectedCertificate) {
      navigator.share({
        title: 'My Achievement',
        text: `I earned a certificate for ${selectedCertificate.goal_title}!`,
      }).catch(console.error);
    }
  };

  if (certificates.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <TrophyIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No Certificates Yet
        </Typography>
        <Typography variant="body2" color="text.disabled">
          Complete goals to earn certificates!
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Grid container spacing={3}>
        {certificates.map((certificate, index) => (
          <Grid item xs={12} sm={6} md={4} key={certificate.id}>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.03 }}
            >
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  border: 2,
                  borderColor: 'warning.light',
                  boxShadow: '0 4px 20px rgba(255, 193, 7, 0.2)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 6px 30px rgba(255, 193, 7, 0.4)',
                    transform: 'translateY(-4px)',
                  },
                }}
                onClick={() => handleCertificateClick(certificate)}
              >
                {/* Certificate Header with Trophy Icon */}
                <CardMedia
                  sx={{
                    height: 180,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                  }}
                >
                  <TrophyIcon sx={{ fontSize: 80, color: 'white', opacity: 0.9 }} />
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 12,
                      right: 12,
                    }}
                  >
                    <VerifiedIcon sx={{ color: 'success.light', fontSize: 32 }} />
                  </Box>
                </CardMedia>

                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Certificate Title */}
                  <Typography variant="h6" fontWeight={700} gutterBottom>
                    {certificate.goal_title || certificate.title}
                  </Typography>

                  {/* Achievement Level */}
                  {certificate.level && (
                    <Chip
                      label={certificate.level}
                      color="warning"
                      size="small"
                      sx={{ mb: 1, fontWeight: 600 }}
                    />
                  )}

                  {/* Earned Date */}
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Earned on {new Date(certificate.earned_date || certificate.created_at).toLocaleDateString()}
                  </Typography>

                  {/* Certificate Number */}
                  {certificate.certificate_number && (
                    <Typography variant="caption" color="text.disabled" sx={{ mt: 1, display: 'block' }}>
                      Certificate #{certificate.certificate_number}
                    </Typography>
                  )}
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    startIcon={<DownloadIcon />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(certificate.id);
                    }}
                  >
                    Download
                  </Button>
                  <Button
                    size="small"
                    startIcon={<ShareIcon />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCertificateClick(certificate);
                    }}
                  >
                    Share
                  </Button>
                </CardActions>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Certificate Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack direction="row" alignItems="center" spacing={1}>
              <TrophyIcon color="warning" />
              <Typography variant="h6">Certificate Details</Typography>
            </Stack>
            <IconButton onClick={() => setDetailDialogOpen(false)} edge="end">
              <CloseIcon />
            </IconButton>
          </Stack>
        </DialogTitle>

        {selectedCertificate && (
          <>
            <DialogContent>
              {/* Certificate Visual */}
              <Box
                sx={{
                  p: 4,
                  mb: 3,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: 2,
                  textAlign: 'center',
                  color: 'white',
                }}
              >
                <TrophyIcon sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h5" fontWeight={700} gutterBottom>
                  Certificate of Achievement
                </Typography>
                <Typography variant="h6" sx={{ mt: 2 }}>
                  {selectedCertificate.goal_title || selectedCertificate.title}
                </Typography>
                <Typography variant="body2" sx={{ mt: 2, opacity: 0.9 }}>
                  Awarded on {new Date(selectedCertificate.earned_date || selectedCertificate.created_at).toLocaleDateString()}
                </Typography>
              </Box>

              {/* Certificate Details */}
              <Stack spacing={2}>
                {selectedCertificate.description && (
                  <Box>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Achievement
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedCertificate.description}
                    </Typography>
                  </Box>
                )}

                {selectedCertificate.certificate_number && (
                  <Box>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Certificate Number
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedCertificate.certificate_number}
                    </Typography>
                  </Box>
                )}

                <Box>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Verification
                  </Typography>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <VerifiedIcon color="success" fontSize="small" />
                    <Typography variant="body2" color="success.main">
                      Verified Certificate
                    </Typography>
                  </Stack>
                </Box>
              </Stack>
            </DialogContent>

            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>
                Close
              </Button>
              <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                onClick={handleShare}
              >
                Share
              </Button>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={() => handleDownload(selectedCertificate.id)}
              >
                Download PDF
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </>
  );
};

CertificateGallery.propTypes = {
  certificates: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      goal_title: PropTypes.string,
      title: PropTypes.string,
      description: PropTypes.string,
      level: PropTypes.string,
      earned_date: PropTypes.string,
      created_at: PropTypes.string,
      certificate_number: PropTypes.string,
    })
  ).isRequired,
};

export default CertificateGallery;
