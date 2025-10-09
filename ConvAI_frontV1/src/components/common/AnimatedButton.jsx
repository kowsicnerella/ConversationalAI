import PropTypes from "prop-types";
import { Button as MuiButton } from "@mui/material";
import { motion } from "framer-motion";

const AnimatedButton = ({
  children,
  variant = "contained",
  color = "primary",
  ...props
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
    >
      <MuiButton variant={variant} color={color} {...props}>
        {children}
      </MuiButton>
    </motion.div>
  );
};

AnimatedButton.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.string,
  color: PropTypes.string,
};

export default AnimatedButton;
