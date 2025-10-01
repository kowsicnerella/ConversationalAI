import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  analyticsAPI,
  coursesAPI,
  userAPI,
  personalizationAPI,
  adaptiveLearningAPI,
} from "../../services/api";
import { useAuthStore } from "../../store";
import LoadingScreen from "../ui/LoadingScreen";
import { toast } from "react-hot-toast";

const AdaptiveLearningDashboard = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const [dashboardData, setDashboardData] = useState(null);
  const [conceptMastery, setConceptMastery] = useState([]);
  const [learningPath, setLearningPath] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch dashboard summary, learning path, and concept mastery
      const [
        dashboardSummary,
        learningPaths,
        userStats,
        personalizationDashboard,
        currentLearningPath,
      ] = await Promise.all([
        analyticsAPI.getDashboardSummary(),
        coursesAPI.getLearningPaths(),
        userAPI.getStatistics(),
        personalizationAPI.getDashboard(),
        adaptiveLearningAPI.getCurrentPath(),
      ]);

      setDashboardData({
        ...dashboardSummary.data.summary,
        ...userStats.data.statistics,
        ...personalizationDashboard.data,
      });

      // Use adaptive learning path if available, otherwise fallback
      if (
        currentLearningPath.data.success &&
        currentLearningPath.data.learning_path
      ) {
        setLearningPath(currentLearningPath.data.learning_path);
      } else if (
        learningPaths.data.learning_paths &&
        learningPaths.data.learning_paths.length > 0
      ) {
        setLearningPath(learningPaths.data.learning_paths[0]);
      }

      // Set concept mastery and recommendations from personalization data
      if (personalizationDashboard.data.success) {
        setConceptMastery(personalizationDashboard.data.concept_mastery || []);
        setRecommendations(personalizationDashboard.data.recommendations || []);
      }
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
      toast.error("Failed to load adaptive learning dashboard");
      // Fallback to basic data
      try {
        const [dashboardSummary, learningPaths, userStats] = await Promise.all([
          analyticsAPI.getDashboardSummary(),
          coursesAPI.getLearningPaths(),
          userAPI.getStatistics(),
        ]);

        setDashboardData({
          ...dashboardSummary.data.summary,
          ...userStats.data.statistics,
        });

        if (
          learningPaths.data.learning_paths &&
          learningPaths.data.learning_paths.length > 0
        ) {
          setLearningPath(learningPaths.data.learning_paths[0]);
        }
      } catch (fallbackError) {
        console.error("Failed to load fallback data:", fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  const startAdaptiveActivity = async () => {
    // For demo, just navigate to the first activity in the current learning path
    if (learningPath && learningPath.id) {
      navigate(`/activity/${learningPath.id}`, {
        state: { adaptiveMode: true },
      });
    }
  };

  const startLearningSession = async (activityId) => {
    // For demo, just navigate to the activity
    navigate(`/activity/${activityId}`, {
      state: {
        adaptiveMode: true,
      },
    });
  };

  const getMasteryColor = (masteryLevel) => {
    switch (masteryLevel) {
      case "mastered":
        return "bg-green-500";
      case "proficient":
        return "bg-blue-500";
      case "developing":
        return "bg-yellow-500";
      case "needs_work":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high":
        return "border-l-red-500 bg-red-50";
      case "medium":
        return "border-l-yellow-500 bg-yellow-50";
      case "low":
        return "border-l-green-500 bg-green-50";
      default:
        return "border-l-gray-500 bg-gray-50";
    }
  };

  if (loading) {
    return (
      <LoadingScreen message="Loading your personalized learning dashboard..." />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Welcome back, {user?.username}! 👋
          </h1>
          <p className="text-gray-600">
            Your AI-powered adaptive learning journey continues
          </p>
        </div>

        {/* Quick Stats */}
        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Overall Progress
                  </p>
                  <p className="text-3xl font-bold text-blue-600">
                    {Math.round(dashboardData.overall_progress_percentage)}%
                  </p>
                </div>
                <div className="text-4xl">📊</div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
                  style={{
                    width: `${dashboardData.overall_progress_percentage}%`,
                  }}
                />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Concepts Mastered
                  </p>
                  <p className="text-3xl font-bold text-green-600">
                    {dashboardData.concepts_mastered}
                  </p>
                </div>
                <div className="text-4xl">🎯</div>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                out of {dashboardData.total_concepts} total
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Learning Streak
                  </p>
                  <p className="text-3xl font-bold text-orange-600">
                    {dashboardData.current_streak}
                  </p>
                </div>
                <div className="text-4xl">🔥</div>
              </div>
              <p className="text-sm text-gray-500 mt-2">days in a row</p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Time This Week
                  </p>
                  <p className="text-3xl font-bold text-purple-600">
                    {Math.round(dashboardData.weekly_study_minutes / 60)}h
                  </p>
                </div>
                <div className="text-4xl">⏰</div>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {dashboardData.weekly_study_minutes} minutes
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Current Learning Path */}
            {learningPath && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  🎯 Current Learning Path
                </h2>

                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">
                    {learningPath.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {learningPath.description}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex space-x-4">
                      <span className="text-sm text-gray-600">
                        Chapter {learningPath.current_chapter} of{" "}
                        {learningPath.total_chapters}
                      </span>
                    </div>
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{
                          width: `${
                            (learningPath.current_chapter /
                              learningPath.total_chapters) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={startAdaptiveActivity}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105"
                  >
                    Continue Learning 🚀
                  </button>

                  <button
                    onClick={() => navigate("/learning-paths")}
                    className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                  >
                    View Full Path
                  </button>
                </div>
              </div>
            )}

            {/* Concept Mastery Overview */}
            {conceptMastery.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  🧠 Concept Mastery
                </h2>

                <div className="space-y-4">
                  {conceptMastery.slice(0, 6).map((concept, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <div
                          className={`w-4 h-4 rounded-full ${getMasteryColor(
                            concept.mastery_level
                          )}`}
                        />
                        <div>
                          <h4 className="font-semibold text-gray-800">
                            {concept.concept} ({concept.skill_area})
                          </h4>
                          <p className="text-sm text-gray-600">
                            {concept.attempts_count} attempts • Last practiced:{" "}
                            {new Date(
                              concept.last_practiced
                            ).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-800">
                          {Math.round(concept.mastery_score * 100)}%
                        </div>
                        <div className="text-sm text-gray-600 capitalize">
                          {concept.mastery_level.replace("_", " ")}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {conceptMastery.length > 6 && (
                  <button
                    onClick={() => navigate("/analytics")}
                    className="w-full mt-4 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View All Concepts →
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* AI Recommendations */}
            {recommendations.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  🤖 AI Recommendations
                </h3>

                <div className="space-y-4">
                  {recommendations.slice(0, 3).map((rec, index) => (
                    <div
                      key={index}
                      className={`p-4 border-l-4 rounded-r-lg ${getPriorityColor(
                        rec.priority
                      )}`}
                    >
                      <h4 className="font-semibold text-gray-800 mb-2">
                        {rec.title}
                      </h4>
                      <p className="text-sm text-gray-600 mb-3">
                        {rec.description}
                      </p>

                      {rec.action_type === "practice_activity" && (
                        <button
                          onClick={() => startLearningSession(rec.activity_id)}
                          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                        >
                          Start Practice →
                        </button>
                      )}

                      {rec.action_type === "review_concept" && (
                        <button
                          onClick={() =>
                            navigate(`/concept-review/${rec.concept_id}`)
                          }
                          className="text-green-600 hover:text-green-700 text-sm font-medium"
                        >
                          Review Concept →
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                ⚡ Quick Actions
              </h3>

              <div className="space-y-3">
                <button
                  onClick={() => navigate("/assessment")}
                  className="w-full bg-purple-100 text-purple-800 px-4 py-3 rounded-lg font-medium hover:bg-purple-200 transition-colors text-left"
                >
                  📝 Take Assessment
                </button>

                <button
                  onClick={() => navigate("/vocabulary")}
                  className="w-full bg-green-100 text-green-800 px-4 py-3 rounded-lg font-medium hover:bg-green-200 transition-colors text-left"
                >
                  📚 Practice Vocabulary
                </button>

                <button
                  onClick={() => navigate("/analytics")}
                  className="w-full bg-blue-100 text-blue-800 px-4 py-3 rounded-lg font-medium hover:bg-blue-200 transition-colors text-left"
                >
                  📊 View Analytics
                </button>

                <button
                  onClick={() => navigate("/chat")}
                  className="w-full bg-yellow-100 text-yellow-800 px-4 py-3 rounded-lg font-medium hover:bg-yellow-200 transition-colors text-left"
                >
                  💬 AI Tutor Chat
                </button>
              </div>
            </div>

            {/* Performance Insights */}
            {dashboardData?.recent_performance && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  📈 Recent Performance
                </h3>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Accuracy Rate</span>
                    <span className="font-semibold text-green-600">
                      {Math.round(
                        dashboardData.recent_performance.accuracy_rate * 100
                      )}
                      %
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Avg. Response Time</span>
                    <span className="font-semibold text-blue-600">
                      {dashboardData.recent_performance.avg_response_time}s
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Difficulty Level</span>
                    <span className="font-semibold text-purple-600 capitalize">
                      {dashboardData.recent_performance.current_difficulty}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdaptiveLearningDashboard;
