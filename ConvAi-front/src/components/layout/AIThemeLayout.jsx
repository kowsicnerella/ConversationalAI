import React from "react";
import { Box, useTheme } from "@mui/material";
import { motion } from "framer-motion";

const AIThemeLayout = ({ children, variant = "default", className = "" }) => {
  const theme = useTheme();

  const variants = {
    default: {
      background:
        theme.palette.mode === "dark"
          ? "linear-gradient(135deg, #0a0f23 0%, #1e293b 100%)"
          : "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    },
    glass: {
      background:
        theme.palette.mode === "dark"
          ? "rgba(30, 41, 59, 0.6)"
          : "rgba(255, 255, 255, 0.8)",
      backdropFilter: "blur(20px)",
      border: `1px solid ${
        theme.palette.mode === "dark"
          ? "rgba(148, 163, 184, 0.1)"
          : "rgba(255, 255, 255, 0.2)"
      }`,
      borderRadius: "24px",
      boxShadow:
        theme.palette.mode === "dark"
          ? "0 8px 32px rgba(0, 0, 0, 0.3)"
          : "0 8px 32px rgba(0, 0, 0, 0.1)",
    },
    gradient: {
      background:
        "linear-gradient(135deg, #4f46e5 0%, #06b6d4 50%, #8b5cf6 100%)",
    },
    neural: {
      background:
        theme.palette.mode === "dark"
          ? "linear-gradient(135deg, #0a0f23 0%, #1e293b 100%)"
          : "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
      backgroundImage:
        theme.palette.mode === "dark"
          ? "radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.1) 1px, transparent 0)"
          : "radial-gradient(circle at 2px 2px, rgba(79, 70, 229, 0.1) 1px, transparent 0)",
      backgroundSize: "40px 40px",
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Box
        sx={{
          ...variants[variant],
          minHeight: "100vh",
          position: "relative",
          overflow: "hidden",
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          px: { xs: 2, sm: 3, md: 4 },
          py: { xs: 2, sm: 3 },
          width: "100%",
          maxWidth: "100vw",
          boxSizing: "border-box",
        }}
        className={`ai-theme-layout ${className}`}
      >
        {variant === "neural" && (
          <Box
            sx={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              opacity: 0.1,
              background: `
                radial-gradient(circle at 20% 80%, rgba(79, 70, 229, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(139, 92, 246, 0.2) 0%, transparent 50%)
              `,
              pointerEvents: "none",
            }}
          />
        )}

        <Box
          sx={{
            position: "relative",
            zIndex: 1,
            width: "100%",
            maxWidth: "100%",
            overflow: "hidden",
          }}
        >
          {children}
        </Box>
      </Box>
    </motion.div>
  );
};

export default AIThemeLayout;
