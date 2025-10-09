import PropTypes from "prop-types";
import { useState, useEffect } from "react";
import { Typography } from "@mui/material";

const TypewriterText = ({ text, speed = 50, delay = 0, ...props }) => {
  const [displayText, setDisplayText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (delay > 0) {
      const delayTimeout = setTimeout(() => {
        setCurrentIndex(0);
      }, delay);
      return () => clearTimeout(delayTimeout);
    }
  }, [delay]);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return (
    <Typography {...props}>
      {displayText}
      {currentIndex < text.length && (
        <span
          style={{
            opacity: 1,
            animation: "blink 1s infinite",
          }}
        >
          |
        </span>
      )}
    </Typography>
  );
};

TypewriterText.propTypes = {
  text: PropTypes.string.isRequired,
  speed: PropTypes.number,
  delay: PropTypes.number,
};

export default TypewriterText;
