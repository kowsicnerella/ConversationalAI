import { motion } from "framer-motion";
import { Box } from "@mui/material";

const LoadingSpinner = () => {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "200px",
      }}
    >
      <motion.div
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: "linear",
        }}
        style={{
          width: 50,
          height: 50,
          border: "4px solid rgba(14, 165, 233, 0.2)",
          borderTop: "4px solid rgb(14, 165, 233)",
          borderRadius: "50%",
        }}
      />
    </Box>
  );
};

export default LoadingSpinner;
