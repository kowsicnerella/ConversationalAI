import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { assessmentAPI, adaptiveLearningAPI } from "../../services/api";
import { useAuthStore } from "../../store";
import LoadingScreen from "../ui/LoadingScreen";

const InitialAssessment = ({ userId }) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [assessment, setAssessment] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [userResponses, setUserResponses] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [audioRecording, setAudioRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const assessmentSteps = [
    { key: "welcome", title: "Welcome", icon: "👋" },
    { key: "vocabulary", title: "Vocabulary", icon: "📚" },
    { key: "grammar", title: "Grammar", icon: "📝" },
    { key: "reading", title: "Reading", icon: "📖" },
    { key: "listening", title: "Listening", icon: "🎧" },
    { key: "writing", title: "Writing", icon: "✍️" },
    { key: "speaking", title: "Speaking", icon: "🗣️" },
    { key: "results", title: "Results", icon: "🎉" },
  ];

  useEffect(() => {
    initializeAssessment();
  }, [userId]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0) {
      handleTimeUp();
    }
  }, [timeRemaining]);

  const initializeAssessment = async () => {
    try {
      setLoading(true);
      const response = await assessmentAPI.startInitialAssessment(
        "comprehensive"
      );
      setAssessment(response.data.assessment || response.data);

      // Get assessment questions
      const questionsResponse = await assessmentAPI.getAssessmentQuestions(
        response.data.assessment_id || response.data.id
      );
      setCurrentQuestion(questionsResponse.data.questions[0]);
      setTimeRemaining(response.data.time_limit || 1800); // 30 minutes default
      setLoading(false);
    } catch (error) {
      console.error("Failed to initialize assessment:", error);
      setError("Failed to start assessment. Please try again.");
      setLoading(false);
    }
  };

  const handleResponse = async (response) => {
    if (!currentQuestion) return;

    const responseData = {
      question_id: currentQuestion.id,
      skill_area: currentQuestion.skill_area,
      response: response,
      timestamp: new Date().toISOString(),
      audio_data: audioBlob ? await blobToBase64(audioBlob) : null,
    };

    setUserResponses((prev) => ({
      ...prev,
      [currentQuestion.id]: responseData,
    }));

    try {
      await assessmentAPI.submitResponse(assessment.id, responseData);
      moveToNextQuestion();
    } catch (error) {
      console.error("Failed to submit response:", error);
      setError("Failed to submit response. Please try again.");
    }
  };

  const moveToNextQuestion = () => {
    const currentSkillQuestions = assessment.questions.filter(
      (q) => q.skill_area === assessmentSteps[currentStep].key
    );
    const currentQuestionIndex = currentSkillQuestions.findIndex(
      (q) => q.id === currentQuestion.id
    );

    if (currentQuestionIndex < currentSkillQuestions.length - 1) {
      // More questions in current skill area
      setCurrentQuestion(currentSkillQuestions[currentQuestionIndex + 1]);
    } else {
      // Move to next skill area
      moveToNextStep();
    }

    setAudioBlob(null);
  };

  const moveToNextStep = () => {
    if (currentStep < assessmentSteps.length - 2) {
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);

      const nextSkillQuestions = assessment.questions.filter(
        (q) => q.skill_area === assessmentSteps[nextStep].key
      );

      if (nextSkillQuestions.length > 0) {
        setCurrentQuestion(nextSkillQuestions[0]);
      } else {
        // No questions for this skill, move to next
        setCurrentStep(nextStep + 1);
      }
    } else {
      // Assessment complete
      completeAssessment();
    }
  };

  const completeAssessment = async () => {
    try {
      setSubmitting(true);
      const response = await assessmentAPI.completeAssessment(assessment.id);

      // Generate personalized learning path
      await adaptiveLearningAPI.generatePersonalizedPath(response.data);

      // Navigate to results or dashboard
      navigate("/assessment-results", {
        state: {
          results: response.data,
          isInitialAssessment: true,
        },
      });
    } catch (error) {
      console.error("Failed to complete assessment:", error);
      setError("Failed to complete assessment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleTimeUp = () => {
    if (Object.keys(userResponses).length > 0) {
      completeAssessment();
    } else {
      setError("Time expired. Please restart the assessment.");
    }
  };

  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav",
        });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setAudioRecording(true);
    } catch (error) {
      console.error("Failed to start recording:", error);
      setError("Microphone access required for speaking assessment.");
    }
  };

  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && audioRecording) {
      mediaRecorderRef.current.stop();
      setAudioRecording(false);
    }
  };

  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (loading) {
    return (
      <LoadingScreen message="Preparing your personalized assessment..." />
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Assessment Error
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-2xl w-full mx-4">
          <div className="text-center">
            <div className="text-6xl mb-6">🎯</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">
              Welcome to Your Personalized Assessment
            </h1>
            <p className="text-gray-600 mb-8 text-lg leading-relaxed">
              This comprehensive assessment will evaluate your current Telugu
              and English skills across multiple areas to create a personalized
              learning path just for you.
            </p>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              {assessmentSteps.slice(1, -1).map((step, index) => (
                <div key={step.key} className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl mb-2">{step.icon}</div>
                  <div className="text-sm font-medium text-gray-700">
                    {step.title}
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <p className="text-blue-800">
                <strong>⏱️ Time Limit:</strong> {formatTime(timeRemaining)}{" "}
                minutes
                <br />
                <strong>📊 Questions:</strong>{" "}
                {assessment?.questions?.length || 0} total
                <br />
                <strong>🎯 Goal:</strong> Create your perfect learning journey
              </p>
            </div>

            <button
              onClick={() => setCurrentStep(1)}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105"
            >
              Start Assessment 🚀
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (submitting) {
    return (
      <LoadingScreen message="Analyzing your responses and creating your personalized learning path..." />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Progress Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="text-2xl">
                {assessmentSteps[currentStep]?.icon}
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">
                  {assessmentSteps[currentStep]?.title} Assessment
                </h2>
                <p className="text-sm text-gray-600">
                  Step {currentStep} of {assessmentSteps.length - 2}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-semibold text-blue-600">
                ⏱️ {formatTime(timeRemaining)}
              </div>
              <div className="text-sm text-gray-600">remaining</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${(currentStep / (assessmentSteps.length - 2)) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Question Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {currentQuestion && (
          <AssessmentQuestion
            question={currentQuestion}
            onResponse={handleResponse}
            audioRecording={audioRecording}
            onStartRecording={startAudioRecording}
            onStopRecording={stopAudioRecording}
            audioBlob={audioBlob}
          />
        )}
      </div>
    </div>
  );
};

// Question Component
const AssessmentQuestion = ({
  question,
  onResponse,
  audioRecording,
  onStartRecording,
  onStopRecording,
  audioBlob,
}) => {
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [writtenResponse, setWrittenResponse] = useState("");

  const handleSubmit = () => {
    let response;

    switch (question.question_type) {
      case "multiple_choice":
        response = selectedAnswer;
        break;
      case "written":
        response = writtenResponse;
        break;
      case "speaking":
        response = audioBlob ? "audio_submitted" : "";
        break;
      default:
        response = selectedAnswer || writtenResponse;
    }

    if (response || audioBlob) {
      onResponse(response);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="mb-6">
        <div className="text-sm text-gray-500 mb-2 uppercase tracking-wide font-medium">
          {question.skill_area} • {question.difficulty_level}
        </div>
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          {question.question_text}
        </h3>

        {question.audio_url && (
          <div className="mb-4">
            <audio controls className="w-full">
              <source src={question.audio_url} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>
          </div>
        )}

        {question.image_url && (
          <div className="mb-4">
            <img
              src={question.image_url}
              alt="Question visual"
              className="max-w-full h-auto rounded-lg shadow-md"
            />
          </div>
        )}
      </div>

      {/* Question Type Specific UI */}
      {question.question_type === "multiple_choice" && (
        <div className="space-y-3 mb-6">
          {question.options?.map((option, index) => (
            <label
              key={index}
              className="flex items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <input
                type="radio"
                name="answer"
                value={option}
                checked={selectedAnswer === option}
                onChange={(e) => setSelectedAnswer(e.target.value)}
                className="mr-3"
              />
              <span className="text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      )}

      {question.question_type === "written" && (
        <div className="mb-6">
          <textarea
            value={writtenResponse}
            onChange={(e) => setWrittenResponse(e.target.value)}
            placeholder="Type your response here..."
            className="w-full h-32 p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      )}

      {question.question_type === "speaking" && (
        <div className="mb-6">
          <div className="text-center">
            {!audioRecording && !audioBlob && (
              <button
                onClick={onStartRecording}
                className="bg-red-500 text-white px-6 py-3 rounded-full hover:bg-red-600 transition-colors"
              >
                🎤 Start Recording
              </button>
            )}

            {audioRecording && (
              <div className="space-y-4">
                <div className="text-red-500 text-lg font-medium animate-pulse">
                  🔴 Recording... Speak now
                </div>
                <button
                  onClick={onStopRecording}
                  className="bg-gray-600 text-white px-6 py-3 rounded-full hover:bg-gray-700 transition-colors"
                >
                  ⏹️ Stop Recording
                </button>
              </div>
            )}

            {audioBlob && (
              <div className="space-y-4">
                <div className="text-green-500 text-lg font-medium">
                  ✅ Recording Complete
                </div>
                <audio controls>
                  <source
                    src={URL.createObjectURL(audioBlob)}
                    type="audio/wav"
                  />
                </audio>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={
            (question.question_type === "multiple_choice" && !selectedAnswer) ||
            (question.question_type === "written" && !writtenResponse.trim()) ||
            (question.question_type === "speaking" && !audioBlob)
          }
          className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
        >
          Continue →
        </button>
      </div>
    </div>
  );
};

export default InitialAssessment;
