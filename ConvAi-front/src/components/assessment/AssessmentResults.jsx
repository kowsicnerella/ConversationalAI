import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { adaptiveLearningAPI } from "../../services/api";
import LoadingScreen from "../ui/LoadingScreen";

const AssessmentResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (location.state?.results) {
      setResults(location.state.results);
      loadLearningPath();
    } else {
      navigate("/dashboard");
    }
  }, [location.state, navigate]);

  const loadLearningPath = async () => {
    try {
      const pathResponse = await adaptiveLearningAPI.getPersonalizedPath();
      setLearningPath(pathResponse.data);
    } catch (error) {
      console.error("Failed to load learning path:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSkillLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case "beginner":
        return "bg-red-100 text-red-800 border-red-200";
      case "intermediate":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "advanced":
        return "bg-green-100 text-green-800 border-green-200";
      case "expert":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return "text-green-600";
    if (score >= 70) return "text-blue-600";
    if (score >= 50) return "text-yellow-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <LoadingScreen message="Analyzing your results and preparing your learning journey..." />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Assessment Complete!
          </h1>
          <p className="text-xl text-gray-600">
            Here are your personalized results and learning recommendations
          </p>
        </div>

        {/* Overall Score */}
        {results && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <div className="text-center">
              <div className="text-6xl font-bold mb-4">
                <span className={getScoreColor(results.overall_score)}>
                  {Math.round(results.overall_score)}%
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Overall Proficiency Level
              </h2>
              <div
                className={`inline-block px-6 py-2 rounded-full border-2 font-semibold text-lg ${getSkillLevelColor(
                  results.proficiency_level
                )}`}
              >
                {results.proficiency_level?.toUpperCase()}
              </div>
            </div>
          </div>
        )}

        {/* Skill Breakdown */}
        {results?.skill_scores && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              Skill Assessment Breakdown
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(results.skill_scores).map(([skill, data]) => (
                <div
                  key={skill}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-800 capitalize">
                      {skill}
                    </h4>
                    <span
                      className={`text-2xl font-bold ${getScoreColor(
                        data.score
                      )}`}
                    >
                      {Math.round(data.score)}%
                    </span>
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-1000 ${
                        data.score >= 85
                          ? "bg-green-500"
                          : data.score >= 70
                          ? "bg-blue-500"
                          : data.score >= 50
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${data.score}%` }}
                    />
                  </div>

                  <div
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSkillLevelColor(
                      data.level
                    )}`}
                  >
                    {data.level}
                  </div>

                  {data.strengths && data.strengths.length > 0 && (
                    <div className="mt-3">
                      <p className="text-sm font-medium text-green-600 mb-1">
                        Strengths:
                      </p>
                      <ul className="text-sm text-gray-600 list-disc list-inside">
                        {data.strengths.slice(0, 2).map((strength, index) => (
                          <li key={index}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {data.areas_for_improvement &&
                    data.areas_for_improvement.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-orange-600 mb-1">
                          Focus Areas:
                        </p>
                        <ul className="text-sm text-gray-600 list-disc list-inside">
                          {data.areas_for_improvement
                            .slice(0, 2)
                            .map((area, index) => (
                              <li key={index}>{area}</li>
                            ))}
                        </ul>
                      </div>
                    )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Learning Path Preview */}
        {learningPath && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              Your Personalized Learning Path
            </h3>

            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
              <div className="flex items-center mb-4">
                <div className="text-3xl mr-4">🎯</div>
                <div>
                  <h4 className="text-xl font-bold text-gray-800">
                    {learningPath.title}
                  </h4>
                  <p className="text-gray-600">{learningPath.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {learningPath.total_chapters}
                  </div>
                  <div className="text-sm text-gray-600">Chapters</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {learningPath.estimated_duration_weeks}w
                  </div>
                  <div className="text-sm text-gray-600">Duration</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {learningPath.difficulty_level}
                  </div>
                  <div className="text-sm text-gray-600">Level</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {learningPath.total_activities}
                  </div>
                  <div className="text-sm text-gray-600">Activities</div>
                </div>
              </div>
            </div>

            {/* First Chapter Preview */}
            {learningPath.chapters && learningPath.chapters.length > 0 && (
              <div className="border rounded-lg p-6">
                <h5 className="text-lg font-bold text-gray-800 mb-3">
                  🚀 Starting with: {learningPath.chapters[0].title}
                </h5>
                <p className="text-gray-600 mb-4">
                  {learningPath.chapters[0].description}
                </p>

                <div className="flex flex-wrap gap-2">
                  {learningPath.chapters[0].focus_areas?.map((area, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Recommendations */}
        {results?.recommendations && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              AI Recommendations
            </h3>
            <div className="space-y-4">
              {results.recommendations.map((recommendation, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg"
                >
                  <div className="text-2xl">💡</div>
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-1">
                      {recommendation.title}
                    </h4>
                    <p className="text-gray-600">
                      {recommendation.description}
                    </p>
                    {recommendation.priority && (
                      <span
                        className={`inline-block mt-2 px-2 py-1 rounded-full text-xs font-medium ${
                          recommendation.priority === "high"
                            ? "bg-red-100 text-red-800"
                            : recommendation.priority === "medium"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {recommendation.priority.toUpperCase()} PRIORITY
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="text-center space-y-4 md:space-y-0 md:space-x-4 md:flex md:justify-center">
          <button
            onClick={() => navigate("/dashboard")}
            className="w-full md:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105"
          >
            Go to Dashboard 🏠
          </button>

          <button
            onClick={() => navigate("/learning-paths")}
            className="w-full md:w-auto bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-300 transform hover:scale-105"
          >
            Start Learning Journey 🚀
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssessmentResults;
