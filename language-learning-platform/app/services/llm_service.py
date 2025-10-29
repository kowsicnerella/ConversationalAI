"""
Lightweight LLMService wrapper

Provides a minimal interface used by services (like PerformanceTrackingEngine)
to request simple analysis or feedback from the configured LLM. This module
avoids importing heavy LLM libraries at module-import time and falls back to
safe no-op behavior when LLMs are not configured (useful for migrations/tests).
"""
from typing import Dict, Any, Optional, List
import json
from app.services.llm_config import LLMConfig, LLMProvider


class LLMService:
    """Simple facade around LLMConfig.

    Methods are intentionally small and defensive so the rest of the app can
    import this class safely even when LLM provider keys or packages are
    missing.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or LLMConfig.DEFAULT_PROVIDER

    def summarize_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Ask the LLM to summarize performance and give suggestions.

        Returns a dictionary with 'summary' and 'suggestions' keys. If the LLM
        is unavailable, return a conservative default.
        """
        try:
            prompt = (
                "Given the following user performance metrics, provide a short "
                "summary (1-2 sentences) and 3 actionable suggestions for improvement. "
                f"Metrics: {performance}"
            )

            resp = LLMConfig.generate_text(prompt, provider=self.provider, json_mode=False)
            if resp.get("success"):
                return {"summary": resp.get("text", ""), "suggestions": []}
            else:
                return {"summary": "", "suggestions": []}
        except Exception:
            # Fail-safe: return empty suggestions so callers can proceed
            return {"summary": "LLM unavailable", "suggestions": []}

    def generate_improvement_suggestions(
        self, 
        skill_type: str,
        performance_data: Dict[str, Any],
        difficulty_level: str = 'intermediate'
    ) -> Dict[str, Any]:
        """Generate structured AI feedback and improvement suggestions.
        
        Args:
            skill_type: Type of skill (listening, speaking, reading, writing, real_world)
            performance_data: Dictionary containing performance metrics
            difficulty_level: Current difficulty level
            
        Returns:
            {
                'feedback': str,  # Overall feedback summary
                'strengths': List[str],  # What the user did well
                'areas_for_improvement': List[str],  # What needs work
                'specific_suggestions': List[str],  # Actionable tips
                'next_steps': List[str]  # Recommended next activities
            }
        """
        try:
            # Extract relevant metrics based on skill type
            score = performance_data.get('overall_score') or performance_data.get('comprehension_score', 0)
            
            prompt = f"""Analyze this {skill_type} performance and provide structured feedback.

Performance Data:
- Skill Type: {skill_type}
- Difficulty Level: {difficulty_level}
- Score: {score}
- Metrics: {json.dumps(performance_data, indent=2)}

Provide feedback in the following JSON format:
{{
    "feedback": "2-3 sentence overall assessment",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "areas_for_improvement": ["area 1", "area 2", "area 3"],
    "specific_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
    "next_steps": ["next step 1", "next step 2"]
}}

Be specific, constructive, and actionable. Focus on practical improvements."""

            resp = LLMConfig.generate_text(
                prompt, 
                provider=self.provider, 
                json_mode=True,
                temperature=0.7
            )
            
            if resp.get("success"):
                try:
                    # Parse JSON response
                    feedback_data = json.loads(resp.get("text", "{}"))
                    
                    # Validate structure
                    required_keys = ['feedback', 'strengths', 'areas_for_improvement', 
                                   'specific_suggestions', 'next_steps']
                    
                    for key in required_keys:
                        if key not in feedback_data:
                            feedback_data[key] = [] if key != 'feedback' else ''
                    
                    return feedback_data
                    
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return self._generate_fallback_feedback(skill_type, score)
            else:
                return self._generate_fallback_feedback(skill_type, score)
                
        except Exception as e:
            print(f"LLM feedback generation failed: {e}")
            return self._generate_fallback_feedback(skill_type, score)
    
    def _generate_fallback_feedback(self, skill_type: str, score: float) -> Dict[str, Any]:
        """Generate basic rule-based feedback when LLM is unavailable"""
        
        if score >= 85:
            level = "excellent"
            strengths = [
                f"Strong performance in {skill_type}",
                "Consistent accuracy",
                "Good mastery of concepts"
            ]
            improvements = [
                "Challenge yourself with harder content",
                "Focus on speed and efficiency",
                "Explore advanced topics"
            ]
        elif score >= 70:
            level = "good"
            strengths = [
                f"Solid understanding of {skill_type}",
                "Making steady progress",
                "Building confidence"
            ]
            improvements = [
                "Practice more complex scenarios",
                "Work on consistency",
                "Review challenging areas"
            ]
        else:
            level = "developing"
            strengths = [
                "Making progress",
                "Building foundations",
                "Showing improvement potential"
            ]
            improvements = [
                "Focus on fundamental concepts",
                "Practice regularly",
                "Review basic principles"
            ]
        
        return {
            'feedback': f"You demonstrated {level} performance in {skill_type} with a score of {score}%. Keep practicing to improve further.",
            'strengths': strengths,
            'areas_for_improvement': improvements,
            'specific_suggestions': [
                f"Practice {skill_type} activities daily for 15-20 minutes",
                "Focus on areas where you struggled",
                "Review and apply feedback from previous sessions"
            ],
            'next_steps': [
                f"Continue with {skill_type} activities at current or slightly higher difficulty",
                "Track your progress over time"
            ]
        }
    
    def analyze_error_patterns(
        self,
        errors: List[Dict[str, Any]],
        skill_type: str
    ) -> Dict[str, Any]:
        """Analyze patterns in user errors to identify systematic issues.
        
        Args:
            errors: List of error dictionaries with details
            skill_type: Type of skill being analyzed
            
        Returns:
            {
                'patterns': List[str],  # Identified error patterns
                'root_causes': List[str],  # Potential root causes
                'targeted_practice': List[str]  # Specific practice recommendations
            }
        """
        try:
            if not errors:
                return {
                    'patterns': [],
                    'root_causes': [],
                    'targeted_practice': []
                }
            
            prompt = f"""Analyze these {skill_type} errors and identify patterns:

Errors: {json.dumps(errors[:10], indent=2)}

Provide analysis in JSON format:
{{
    "patterns": ["pattern 1", "pattern 2"],
    "root_causes": ["cause 1", "cause 2"],
    "targeted_practice": ["practice 1", "practice 2"]
}}

Focus on recurring mistakes and underlying issues."""

            resp = LLMConfig.generate_text(
                prompt,
                provider=self.provider,
                json_mode=True,
                temperature=0.6
            )
            
            if resp.get("success"):
                try:
                    return json.loads(resp.get("text", "{}"))
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            return {
                'patterns': ["Multiple errors detected"],
                'root_causes': ["Needs more practice"],
                'targeted_practice': [f"Focus on {skill_type} fundamentals"]
            }
            
        except Exception:
            return {
                'patterns': [],
                'root_causes': [],
                'targeted_practice': []
            }
