import { Box, CircularProgress, Typography } from "@mui/material";
import { motion } from "framer-motion";

const LoadingScreen = ({ message = "Loading...", size = 60 }) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <CircularProgress
          size={size}
          thickness={4}
          sx={{ color: "#fff", mb: 2 }}
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <Typography
          variant="h6"
          sx={{
            color: "#fff",
            fontWeight: 300,
            textAlign: "center",
          }}
        >
          {message}
        </Typography>
      </motion.div>
    </Box>
  );
};

export default LoadingScreen;
