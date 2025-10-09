import PropTypes from "prop-types";
import { motion } from "framer-motion";
import { Typography } from "@mui/material";

const GradientText = ({ children, variant = "h1", className, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <Typography
        variant={variant}
        className={`gradient-text ${className}`}
        sx={{
          background:
            "linear-gradient(90deg, #0ea5e9 0%, #d946ef 50%, #0ea5e9 100%)",
          backgroundSize: "200% auto",
          backgroundClip: "text",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          animation: "gradient 3s ease infinite",
          ...props.sx,
        }}
        {...props}
      >
        {children}
      </Typography>
    </motion.div>
  );
};

GradientText.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.string,
  className: PropTypes.string,
  sx: PropTypes.object,
};

export default GradientText;
