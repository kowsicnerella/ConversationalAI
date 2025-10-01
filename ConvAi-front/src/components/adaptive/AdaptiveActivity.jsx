import { useState, useEffect, useRef } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { adaptiveLearningAPI, activityAPI } from "../../services/api";
import { useAuthStore } from "../../store";
import LoadingScreen from "../ui/LoadingScreen";

const AdaptiveActivity = () => {
  const { activityId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  const [activity, setActivity] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [adaptiveMode, setAdaptiveMode] = useState(false);
  const [hints, setHints] = useState([]);
  const [showHint, setShowHint] = useState(false);
  const [performance, setPerformance] = useState(null);
  const [interventionActive, setInterventionActive] = useState(false);

  const startTime = useRef(Date.now());
  const questionStartTime = useRef(Date.now());

  useEffect(() => {
    if (location.state?.sessionId) {
      setSessionId(location.state.sessionId);
      setAdaptiveMode(location.state.adaptiveMode || false);
    }
    loadActivity();
  }, [activityId, location.state]);

  useEffect(() => {
    if (adaptiveMode && sessionId && activity) {
      // Track user interaction
      trackInteraction("activity_started", {
        activity_id: activityId,
        total_questions: activity.questions?.length || 0,
      });
    }
  }, [adaptiveMode, sessionId, activity, activityId]);

  const loadActivity = async () => {
    try {
      setLoading(true);

      let activityData;
      if (adaptiveMode) {
        // Get next adaptive activity
        const response = await adaptiveLearningAPI.getNextActivity(activityId);
        activityData = response.data;
      } else {
        // Get regular activity
        const response = await activityAPI.getPathActivities(activityId);
        activityData = response.data;
      }

      setActivity(activityData);
      setCurrentQuestion(0);
      setUserAnswers([]);
      questionStartTime.current = Date.now();
    } catch (error) {
      console.error("Failed to load activity:", error);
    } finally {
      setLoading(false);
    }
  };

  const trackInteraction = async (interactionType, data = {}) => {
    if (!adaptiveMode || !sessionId) return;

    try {
      const interactionData = {
        interaction_type: interactionType,
        timestamp: new Date().toISOString(),
        response_time: Date.now() - questionStartTime.current,
        question_index: currentQuestion,
        ...data,
      };

      await adaptiveLearningAPI.trackUserInteraction(
        sessionId,
        interactionData
      );

      // Check if intervention is needed
      if (interactionType === "answer_submitted" && data.is_correct === false) {
        checkForIntervention();
      }
    } catch (error) {
      console.error("Failed to track interaction:", error);
    }
  };

  const checkForIntervention = async () => {
    try {
      const recentAnswers = userAnswers.slice(-3); // Last 3 answers
      const incorrectCount = recentAnswers.filter((a) => !a.is_correct).length;

      if (incorrectCount >= 2) {
        const sessionData = {
          recent_performance: recentAnswers,
          current_question: currentQuestion,
          struggling_concept: activity.questions[currentQuestion]?.concept,
        };

        // For now, disable intervention checks as the API may not be fully implemented
        // const response = await adaptiveLearningAPI.checkInterventionNeeds(
        //   user.id,
        //   sessionData
        // );
        const response = { data: { intervention_needed: false } };

        if (response.data.intervention_needed) {
          setInterventionActive(true);
          await generateHints();
        }
      }
    } catch (error) {
      console.error("Failed to check intervention needs:", error);
    }
  };

  const generateHints = async () => {
    try {
      const strugglingConcept = activity.questions[currentQuestion]?.concept;
      // For now, provide generic hints as the API may not be fully implemented
      // const response = await adaptiveLearningAPI.getPersonalizedHints(
      //   user.id,
      //   activityId,
      //   strugglingConcept
      // );
      const response = {
        data: {
          hints: [
            "Take your time to read the question carefully.",
            "Try to eliminate obviously wrong answers first.",
          ],
        },
      };

      setHints(response.data.hints || []);
    } catch (error) {
      console.error("Failed to generate hints:", error);
    }
  };

  const handleAnswer = async (answer, isCorrect) => {
    const responseTime = Date.now() - questionStartTime.current;

    const answerData = {
      question_index: currentQuestion,
      question_id: activity.questions[currentQuestion]?.id,
      user_answer: answer,
      correct_answer: activity.questions[currentQuestion]?.correct_answer,
      is_correct: isCorrect,
      response_time: responseTime,
      timestamp: new Date().toISOString(),
      hints_used: showHint,
    };

    setUserAnswers((prev) => [...prev, answerData]);

    // Track interaction in adaptive mode
    await trackInteraction("answer_submitted", {
      is_correct: isCorrect,
      response_time: responseTime,
      hints_used: showHint,
    });

    // Reset for next question
    setShowHint(false);
    setHints([]);
    setInterventionActive(false);
    questionStartTime.current = Date.now();

    // Move to next question or complete activity
    if (currentQuestion < (activity.questions?.length || 0) - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      await completeActivity();
    }
  };

  const completeActivity = async () => {
    try {
      setSubmitting(true);

      const totalTime = Date.now() - startTime.current;
      const correctAnswers = userAnswers.filter((a) => a.is_correct).length;
      const accuracy = correctAnswers / userAnswers.length;

      const completionData = {
        activity_id: activityId,
        user_answers: userAnswers,
        total_time: totalTime,
        accuracy: accuracy,
        completion_timestamp: new Date().toISOString(),
      };

      if (adaptiveMode && sessionId) {
        // End adaptive learning session
        await adaptiveLearningAPI.endLearningSession(sessionId, completionData);

        // Get session performance data
        const perfResponse = await adaptiveLearningAPI.getSessionPerformance(
          sessionId
        );
        setPerformance(perfResponse.data);

        // Navigate to adaptive results
        navigate("/activity-results", {
          state: {
            results: completionData,
            performance: perfResponse.data,
            adaptiveMode: true,
          },
        });
      } else {
        // Regular activity completion
        await activityAPI.saveActivity(completionData);
        navigate("/activities");
      }
    } catch (error) {
      console.error("Failed to complete activity:", error);
    } finally {
      setSubmitting(false);
    }
  };

  const requestHint = () => {
    setShowHint(true);
    trackInteraction("hint_requested", {
      question_index: currentQuestion,
    });
  };

  if (loading) {
    return <LoadingScreen message="Loading your personalized activity..." />;
  }

  if (submitting) {
    return (
      <LoadingScreen message="Processing your results and updating your learning path..." />
    );
  }

  if (!activity || !activity.questions) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-xl shadow-lg text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Activity Not Found
          </h2>
          <button
            onClick={() => navigate("/activities")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Activities
          </button>
        </div>
      </div>
    );
  }

  const question = activity.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / activity.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                {activity.title}
              </h1>
              <p className="text-gray-600">
                Question {currentQuestion + 1} of {activity.questions.length}
                {adaptiveMode && (
                  <span className="ml-2 text-blue-600">• Adaptive Mode</span>
                )}
              </p>
            </div>

            {adaptiveMode && (
              <div className="text-right">
                <div className="text-sm text-gray-600">Session Performance</div>
                <div className="text-lg font-semibold text-blue-600">
                  {userAnswers.length > 0
                    ? `${Math.round(
                        (userAnswers.filter((a) => a.is_correct).length /
                          userAnswers.length) *
                          100
                      )}%`
                    : "-"}
                </div>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-600 to-indigo-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Question Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Intervention Notice */}
          {interventionActive && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-2">
                <div className="text-2xl mr-3">🤖</div>
                <h3 className="text-lg font-semibold text-orange-800">
                  AI Tutor Assistant
                </h3>
              </div>
              <p className="text-orange-700">
                I notice you're having some difficulty with this concept. Let me
                help you!
              </p>
            </div>
          )}

          {/* Question */}
          <div className="mb-6">
            <div className="text-sm text-gray-500 mb-2 uppercase tracking-wide font-medium">
              {question.skill_area} • {question.difficulty_level}
              {question.concept && <span> • {question.concept}</span>}
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              {question.question_text}
            </h2>

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

          {/* Hints */}
          {showHint && hints.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-2">
                <div className="text-xl mr-2">💡</div>
                <h4 className="font-semibold text-blue-800">Hint</h4>
              </div>
              <div className="space-y-2">
                {hints.map((hint, index) => (
                  <p key={index} className="text-blue-700">
                    {hint}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Question Component based on type */}
          <QuestionRenderer
            question={question}
            onAnswer={handleAnswer}
            adaptiveMode={adaptiveMode}
            onHintRequest={requestHint}
            showHint={showHint}
            interventionActive={interventionActive}
          />
        </div>
      </div>
    </div>
  );
};

// Question Renderer Component
const QuestionRenderer = ({
  question,
  onAnswer,
  adaptiveMode,
  onHintRequest,
  showHint,
  interventionActive,
}) => {
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [writtenResponse, setWrittenResponse] = useState("");

  const handleSubmit = () => {
    let answer,
      isCorrect = false;

    switch (question.question_type) {
      case "multiple_choice":
        answer = selectedAnswer;
        isCorrect = selectedAnswer === question.correct_answer;
        break;
      case "written":
        answer = writtenResponse;
        // For written responses, we'll need AI evaluation
        isCorrect = true; // Placeholder - should be evaluated by AI
        break;
      default:
        answer = selectedAnswer || writtenResponse;
        isCorrect = answer === question.correct_answer;
    }

    if (answer) {
      onAnswer(answer, isCorrect);
    }
  };

  return (
    <div>
      {/* Multiple Choice */}
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

      {/* Written Response */}
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

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-4">
          {adaptiveMode && !showHint && (
            <button
              onClick={onHintRequest}
              className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-lg hover:bg-yellow-200 transition-colors"
            >
              💡 Need a Hint?
            </button>
          )}

          {interventionActive && (
            <div className="text-sm text-orange-600 font-medium">
              🤖 AI assistance available
            </div>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={
            (question.question_type === "multiple_choice" && !selectedAnswer) ||
            (question.question_type === "written" && !writtenResponse.trim())
          }
          className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
        >
          Submit Answer →
        </button>
      </div>
    </div>
  );
};

export default AdaptiveActivity;
