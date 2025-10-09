import PropTypes from "prop-types";
import { Box, CircularProgress, Typography, Stack } from "@mui/material";
import { motion } from "framer-motion";

const LoadingState = ({ message = "Loading...", size = 60 }) => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="60vh"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <Stack spacing={2} alignItems="center">
          <CircularProgress size={size} thickness={4} />
          {message && (
            <Typography variant="body1" color="text.secondary">
              {message}
            </Typography>
          )}
        </Stack>
      </motion.div>
    </Box>
  );
};

LoadingState.propTypes = {
  message: PropTypes.string,
  size: PropTypes.number,
};

export default LoadingState;
