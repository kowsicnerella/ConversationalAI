import PropTypes from "prop-types";
import { Card as MuiCard } from "@mui/material";
import { motion } from "framer-motion";

const GlassCard = ({ children, className, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -5 }}
    >
      <MuiCard
        className={`glass-effect ${className}`}
        sx={{
          background: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
          ...props.sx,
        }}
        {...props}
      >
        {children}
      </MuiCard>
    </motion.div>
  );
};

GlassCard.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  sx: PropTypes.object,
};

export default GlassCard;
