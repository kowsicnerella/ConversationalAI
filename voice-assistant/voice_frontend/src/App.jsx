import React, { useState } from "react";

function App() {
  const [message, setMessage] = useState("Click the mic to speak");
  const [isListening, setIsListening] = useState(false);
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  const synth = window.speechSynthesis;

  const handleListen = () => {
    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser!");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();
    setIsListening(true);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMessage(`You said: ${transcript}`);

      // Simple example response (your friend will connect backend later)
      let reply = "";
      if (transcript.toLowerCase().includes("hello")) {
        reply = "Hi there! How can I help you?";
      } else if (transcript.toLowerCase().includes("time")) {
        reply = `The time is ${new Date().toLocaleTimeString()}`;
      } else {
        reply = "Sorry, I didn't understand that.";
      }

      speak(reply);
    };

    recognition.onerror = (event) => {
      console.error(event.error);
      setMessage("Error occurred: " + event.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);
  };

  const speak = (text) => {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    synth.speak(utter);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🎤 Voice Assistant</h1>
      <p style={styles.message}>{message}</p>
      <button
        style={{
          ...styles.button,
          backgroundColor: isListening ? "#ff4d4d" : "#4CAF50",
        }}
        onClick={handleListen}
      >
        {isListening ? "Listening..." : "🎙️ Start Listening"}
      </button>
    </div>
  );
}

const styles = {
  container: {
    height: "100%",           // full height of root
    width: "100%",            // full width
    display: "flex",
    flexDirection: "column",
    justifyContent: "center", // vertical centering
    alignItems: "center",     // horizontal centering
    fontFamily: "Arial, sans-serif",
    background: "linear-gradient(to right, #8360c3, #2ebf91)",
    color: "#fff",
    textAlign: "center",
    padding: "0 20px",        // responsive padding for smaller screens
    boxSizing: "border-box",
  },
  title: { fontSize: "3rem", marginBottom: "20px" },
  message: { fontSize: "1.2rem", marginBottom: "30px" },
  button: {
    fontSize: "1.2rem",
    padding: "15px 30px",
    borderRadius: "30px",
    border: "none",
    cursor: "pointer",
    color: "#fff",
    minWidth: "200px",
  },
};

export default App;
