import React, { useState, useRef } from "react";

function App() {
  const [message, setMessage] = useState("Click the mic to speak");
  const [isListening, setIsListening] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // --- send audio to Flask backend ---
  async function sendAudio(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "user_audio.wav");

    const response = await fetch("http://127.0.0.1:5000/process-audio", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    console.log("LLM Reply:", data.reply_text);
    setMessage("Assistant: " + data.reply_text);

    // Play the TTS audio reply
    const audio = new Audio("http://127.0.0.1:5000/get-audio");
    audio.play();
  }

  // --- start recording ---
  const handleListen = async () => {
    if (isListening) return;
    setMessage("Listening...");
    setIsListening(true);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);
    audioChunksRef.current = [];

    mediaRecorderRef.current.ondataavailable = (event) => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      await sendAudio(audioBlob);
      setIsListening(false);
    };

    mediaRecorderRef.current.start();

    // Auto-stop after 5 seconds (you can adjust this)
    setTimeout(() => {
      mediaRecorderRef.current.stop();
    }, 5000);
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
    height: "100%",
    width: "100%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "Arial, sans-serif",
    background: "linear-gradient(to right, #8360c3, #2ebf91)",
    color: "#fff",
    textAlign: "center",
    padding: "0 20px",
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
