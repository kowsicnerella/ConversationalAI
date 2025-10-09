import { useEffect } from "react";
import PropTypes from "prop-types";
import {
  Dialog,
  DialogContent,
  Box,
  Typography,
  IconButton,
  Button,
} from "@mui/material";
import { Close as CloseIcon } from "@mui/icons-material";
import { motion } from "framer-motion";
import Confetti from "react-confetti";
import { useWindowSize } from "react-use";

const MilestoneModal = ({ open, onClose, milestone }) => {
  const { width, height } = useWindowSize();
  const showConfetti = open && milestone;

  useEffect(() => {
    if (open && milestone) {
      // Play celebration sound (optional)
      // const audio = new Audio('/celebration.mp3');
      // audio.play();
    }
  }, [open, milestone]);

  if (!milestone) return null;

  const getMilestoneColor = (color) => {
    const colorMap = {
      gold: "#FFD700",
      success: "#4CAF50",
      orange: "#FF9800",
      blue: "#2196F3",
      purple: "#9C27B0",
    };
    return colorMap[color] || "#FFD700";
  };

  return (
    <>
      {showConfetti && (
        <Confetti
          width={width}
          height={height}
          recycle={false}
          numberOfPieces={500}
          gravity={0.3}
        />
      )}

      <Dialog
        open={open}
        onClose={onClose}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            overflow: "visible",
            background: `linear-gradient(135deg, ${getMilestoneColor(
              milestone.color
            )}15 0%, ${getMilestoneColor(milestone.color)}30 100%)`,
          },
        }}
      >
        <IconButton
          onClick={onClose}
          sx={{
            position: "absolute",
            right: 8,
            top: 8,
            zIndex: 1,
          }}
        >
          <CloseIcon />
        </IconButton>

        <DialogContent sx={{ textAlign: "center", py: 6, px: 4 }}>
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: "spring",
              stiffness: 260,
              damping: 20,
            }}
          >
            <Box
              sx={{
                fontSize: "120px",
                mb: 2,
                filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.2))",
              }}
            >
              {milestone.icon}
            </Box>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Typography
              variant="h3"
              gutterBottom
              fontWeight={700}
              sx={{
                background: `linear-gradient(45deg, ${getMilestoneColor(
                  milestone.color
                )}, #667eea)`,
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              {milestone.title}
            </Typography>

            <Typography variant="h5" color="text.secondary" gutterBottom>
              {milestone.telugu_title}
            </Typography>

            <Typography
              variant="body1"
              sx={{ mt: 3, mb: 2, fontSize: "1.1rem" }}
            >
              {milestone.description}
            </Typography>

            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mb: 4, fontSize: "1.1rem" }}
            >
              {milestone.telugu_description}
            </Typography>

            {milestone.points_awarded > 0 && (
              <Box
                sx={{
                  display: "inline-block",
                  bgcolor: getMilestoneColor(milestone.color) + "20",
                  px: 3,
                  py: 1.5,
                  borderRadius: 2,
                  mb: 3,
                }}
              >
                <Typography variant="h5" fontWeight={600}>
                  🎁 +{milestone.points_awarded} Points
                </Typography>
              </Box>
            )}

            <Box mt={4}>
              <Button
                variant="contained"
                size="large"
                onClick={onClose}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                  background: `linear-gradient(45deg, ${getMilestoneColor(
                    milestone.color
                  )}, #667eea)`,
                  "&:hover": {
                    background: `linear-gradient(45deg, ${getMilestoneColor(
                      milestone.color
                    )}dd, #667eeadd)`,
                  },
                }}
              >
                Continue Learning
              </Button>
            </Box>
          </motion.div>
        </DialogContent>
      </Dialog>
    </>
  );
};

MilestoneModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  milestone: PropTypes.shape({
    icon: PropTypes.string,
    title: PropTypes.string,
    telugu_title: PropTypes.string,
    description: PropTypes.string,
    telugu_description: PropTypes.string,
    color: PropTypes.string,
    points_awarded: PropTypes.number,
  }),
};

export default MilestoneModal;
