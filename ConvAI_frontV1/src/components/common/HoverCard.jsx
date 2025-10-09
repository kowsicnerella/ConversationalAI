import PropTypes from "prop-types";
import { Card } from "@mui/material";
import { motion } from "framer-motion";

const HoverCard = ({ children, elevation = 2, ...props }) => {
  return (
    <motion.div
      whileHover={{
        y: -8,
        transition: { duration: 0.3 },
      }}
    >
      <Card
        elevation={elevation}
        sx={{
          height: "100%",
          transition: "all 0.3s ease",
          cursor: "pointer",
          "&:hover": {
            boxShadow: 6,
          },
          ...props.sx,
        }}
        {...props}
      >
        {children}
      </Card>
    </motion.div>
  );
};

HoverCard.propTypes = {
  children: PropTypes.node.isRequired,
  elevation: PropTypes.number,
  sx: PropTypes.object,
};

export default HoverCard;
