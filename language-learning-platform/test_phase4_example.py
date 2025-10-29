"""
Phase 4: Example Usage Script
Demonstrates how to use the Performance Tracking API endpoints
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api/performance"
# Replace with actual JWT token after authentication
AUTH_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()


# ==================== EXAMPLE 1: Track Listening Performance ====================

def example_track_listening():
    """Example: Track listening comprehension performance"""
    print("\n🎧 EXAMPLE 1: Tracking Listening Performance")
    
    payload = {
        "activity_id": 1,
        "session_id": "session-12345",
        "audio_duration": 180.0,
        "audio_url": "https://example.com/audio/business-meeting.mp3",
        "accent_type": "american",
        "speed_factor": 1.0,
        "topic": "Business Meetings",
        "difficulty_level": "intermediate",
        "comprehension_score": 85.5,
        "accuracy_percentage": 87.0,
        "playback_count": 2,
        "pause_points": [30.5, 45.2, 90.1, 120.5],
        "replay_sections": [[20, 35], [80, 95]],
        "difficult_segments": [{"start": 60, "end": 75, "reason": "Fast speech"}],
        "difficult_words": ["negotiation", "stakeholder", "synergy"],
        "new_vocabulary": ["paradigm", "leverage", "bandwidth"],
        "context_understanding": 82.0,
        "inference_ability": 78.0,
        "total_questions": 10,
        "correct_answers": 8,
        "time_to_complete": 300,
        "avg_time_per_question": 30.0,
        "weak_phonemes": ["th", "r"],
        "accent_adaptation_score": 80.0
    }
    
    response = requests.post(
        f"{BASE_URL}/listening",
        json=payload,
        headers=headers
    )
    
    print_response("Track Listening Performance", response)
    return response.json() if response.status_code == 201 else None


# ==================== EXAMPLE 2: Track Speaking Performance ====================

def example_track_speaking():
    """Example: Track speaking performance"""
    print("\n🗣️ EXAMPLE 2: Tracking Speaking Performance")
    
    payload = {
        "activity_id": 2,
        "session_id": "session-12346",
        "speaking_type": "presentation",
        "topic": "Technology Trends",
        "scenario": "Give a 2-minute presentation on AI trends",
        "difficulty_level": "advanced",
        "audio_url": "https://example.com/recordings/user-presentation.mp3",
        "recording_duration": 125.0,
        "transcript": "Today I want to discuss artificial intelligence trends...",
        "expected_content": "Technology, AI, future predictions",
        "pronunciation_accuracy": 88.0,
        "fluency_score": 85.0,
        "grammar_score": 90.0,
        "vocabulary_richness": 82.0,
        "overall_score": 86.3,
        "words_per_minute": 140,
        "speaking_rate": "normal",
        "hesitation_count": 3,
        "filler_words": ["um", "uh", "like"],
        "filler_word_count": 3,
        "pause_analysis": {
            "total_pauses": 8,
            "avg_pause_duration": 0.8,
            "natural_pauses": 6,
            "hesitation_pauses": 2
        },
        "mispronounced_words": ["algorithm", "neural"],
        "phoneme_errors": ["th", "l"],
        "accent_score": 85.0,
        "intonation_score": 88.0,
        "grammar_errors": [
            {"error": "tense", "example": "I goes instead of I go"}
        ],
        "vocabulary_used": ["artificial intelligence", "machine learning", "automation"],
        "advanced_vocabulary_count": 12,
        "confidence_level": 75.0,
        "volume_consistency": 82.0,
        "content_relevance": 90.0,
        "coherence_score": 87.0,
        "task_completion": 95.0
    }
    
    response = requests.post(
        f"{BASE_URL}/speaking",
        json=payload,
        headers=headers
    )
    
    print_response("Track Speaking Performance", response)
    return response.json() if response.status_code == 201 else None


# ==================== EXAMPLE 3: Track Reading Performance ====================

def example_track_reading():
    """Example: Track reading comprehension performance"""
    print("\n📚 EXAMPLE 3: Tracking Reading Performance")
    
    payload = {
        "activity_id": 3,
        "session_id": "session-12347",
        "text_title": "The Future of Renewable Energy",
        "text_type": "article",
        "topic": "Science & Technology",
        "difficulty_level": "advanced",
        "word_count": 650,
        "text_complexity": 8.5,
        "reading_time_seconds": 240,
        "reading_speed_wpm": 162,
        "speed_rating": "good",
        "target_speed_wpm": 200,
        "comprehension_score": 88.0,
        "accuracy_percentage": 90.0,
        "literal_comprehension": 92.0,
        "inferential_comprehension": 85.0,
        "critical_comprehension": 87.0,
        "vocabulary_lookups": ["photovoltaic", "turbine", "sustainable"],
        "lookup_count": 3,
        "re_read_sections": [[2, 3], [5, 5]],
        "re_read_count": 2,
        "time_per_paragraph": [30, 35, 28, 32, 35, 28, 30, 22],
        "total_questions": 12,
        "correct_answers": 10,
        "time_per_question": [15, 18, 12, 20, 16, 14, 22, 18, 15, 17, 19, 14],
        "avg_time_per_question": 16.7,
        "new_vocabulary_encountered": ["photovoltaic", "geothermal", "biomass"],
        "unknown_words": ["photovoltaic"],
        "vocabulary_coverage": 97.5,
        "main_idea_understanding": 92.0,
        "detail_retention": 85.0,
        "inference_ability": 87.0,
        "context_clue_usage": 83.0
    }
    
    response = requests.post(
        f"{BASE_URL}/reading",
        json=payload,
        headers=headers
    )
    
    print_response("Track Reading Performance", response)
    return response.json() if response.status_code == 201 else None


# ==================== EXAMPLE 4: Track Writing Performance ====================

def example_track_writing():
    """Example: Track writing performance"""
    print("\n✍️ EXAMPLE 4: Tracking Writing Performance")
    
    payload = {
        "activity_id": 4,
        "session_id": "session-12348",
        "writing_type": "essay",
        "topic": "Climate Change Solutions",
        "prompt": "Write a 300-word essay on practical solutions to climate change",
        "difficulty_level": "intermediate",
        "target_word_count": 300,
        "content": "Climate change is one of the most pressing...",  # Truncated for example
        "word_count": 312,
        "character_count": 1856,
        "paragraph_count": 4,
        "sentence_count": 18,
        "overall_score": 84.0,
        "grammar_score": 88.0,
        "vocabulary_score": 82.0,
        "coherence_score": 86.0,
        "task_achievement": 90.0,
        "grammar_errors": [
            {"type": "article", "original": "an renewable", "corrected": "a renewable"}
        ],
        "grammar_error_count": 1,
        "error_types": {"article": 1},
        "spelling_errors": [],
        "spelling_error_count": 0,
        "punctuation_errors": [],
        "punctuation_error_count": 0,
        "vocabulary_used": ["climate", "renewable", "sustainable", "emissions"],
        "unique_words": 145,
        "advanced_vocabulary": ["mitigation", "adaptation", "infrastructure"],
        "advanced_vocabulary_count": 8,
        "vocabulary_diversity": 85.0,
        "vocabulary_appropriateness": 88.0,
        "repetitive_words": ["climate", "energy"],
        "sentence_lengths": [15, 18, 12, 20, 16, 14, 22, 18, 15, 17, 19, 14, 16, 21, 13, 17, 19, 15],
        "avg_sentence_length": 17.3,
        "sentence_variety": 82.0,
        "simple_sentences": 6,
        "compound_sentences": 8,
        "complex_sentences": 4,
        "sentence_complexity": 75.0,
        "paragraph_organization": 88.0,
        "transition_usage": 80.0,
        "topic_consistency": 92.0,
        "argument_development": 85.0,
        "originality_score": 78.0,
        "depth_of_content": 82.0,
        "relevance_to_prompt": 95.0,
        "supporting_evidence": 80.0,
        "writing_time_minutes": 25,
        "revision_count": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/writing",
        json=payload,
        headers=headers
    )
    
    print_response("Track Writing Performance", response)
    return response.json() if response.status_code == 201 else None


# ==================== EXAMPLE 5: Track Real-World Performance ====================

def example_track_real_world():
    """Example: Track real-world scenario performance"""
    print("\n💼 EXAMPLE 5: Tracking Real-World Performance")
    
    payload = {
        "activity_id": 5,
        "session_id": "session-12349",
        "scenario_type": "email",
        "industry": "business",
        "context": "Write a professional follow-up email to a client",
        "difficulty_level": "intermediate",
        "task_description": "Send a follow-up email after a business meeting",
        "expected_outcomes": ["professional tone", "clear action items", "appropriate closing"],
        "user_response": "Dear Mr. Johnson, Following up on our meeting...",
        "response_format": "written",
        "overall_score": 87.0,
        "task_completion": 92.0,
        "appropriateness_score": 90.0,
        "professional_language_use": 88.0,
        "cultural_awareness": 85.0,
        "clarity_score": 90.0,
        "persuasiveness": 83.0,
        "diplomacy_score": 88.0,
        "engagement_quality": 85.0,
        "vocabulary_appropriateness": 90.0,
        "grammar_accuracy": 92.0,
        "register_appropriateness": 88.0,
        "idiomatic_usage": 82.0,
        "email_etiquette_score": 90.0,
        "time_management": 85.0,
        "response_time_seconds": 480,
        "expected_time_seconds": 600,
        "strengths": [
            "Clear and professional tone",
            "Well-structured email",
            "Appropriate greeting and closing"
        ],
        "weaknesses": [
            "Could be more concise",
            "Missing specific deadline"
        ],
        "mistakes_made": ["Slightly too formal for context"],
        "best_practices_followed": ["Clear subject line", "Action items listed"],
        "best_practices_missed": ["Could add a specific deadline"],
        "skills_demonstrated": ["Professional communication", "Email etiquette"],
        "skills_to_develop": ["Conciseness", "Time management"],
        "real_world_readiness": 88.0,
        "confidence_level": 80.0
    }
    
    response = requests.post(
        f"{BASE_URL}/real-world",
        json=payload,
        headers=headers
    )
    
    print_response("Track Real-World Performance", response)
    return response.json() if response.status_code == 201 else None


# ==================== EXAMPLE 6: Get Skill Trajectory ====================

def example_get_trajectory():
    """Example: Get skill trajectory analysis"""
    print("\n📈 EXAMPLE 6: Getting Skill Trajectory")
    
    response = requests.get(
        f"{BASE_URL}/trajectory/listening?time_window_days=30",
        headers=headers
    )
    
    print_response("Skill Trajectory Analysis", response)
    return response.json() if response.status_code == 200 else None


# ==================== EXAMPLE 7: Get Learning Patterns ====================

def example_get_patterns():
    """Example: Identify learning patterns"""
    print("\n🔍 EXAMPLE 7: Identifying Learning Patterns")
    
    response = requests.get(
        f"{BASE_URL}/patterns",
        headers=headers
    )
    
    print_response("Learning Patterns Analysis", response)
    return response.json() if response.status_code == 200 else None


# ==================== EXAMPLE 8: Predict Mastery Timeline ====================

def example_predict_mastery():
    """Example: Predict mastery timeline"""
    print("\n🎯 EXAMPLE 8: Predicting Mastery Timeline")
    
    response = requests.get(
        f"{BASE_URL}/mastery-prediction/speaking",
        headers=headers
    )
    
    print_response("Mastery Prediction", response)
    return response.json() if response.status_code == 200 else None


# ==================== EXAMPLE 9: Get Performance History ====================

def example_get_history():
    """Example: Get performance history"""
    print("\n📜 EXAMPLE 9: Getting Performance History")
    
    response = requests.get(
        f"{BASE_URL}/history/listening?limit=10&offset=0",
        headers=headers
    )
    
    print_response("Performance History", response)
    return response.json() if response.status_code == 200 else None


# ==================== EXAMPLE 10: Get Dashboard ====================

def example_get_dashboard():
    """Example: Get comprehensive performance dashboard"""
    print("\n📊 EXAMPLE 10: Getting Performance Dashboard")
    
    response = requests.get(
        f"{BASE_URL}/dashboard",
        headers=headers
    )
    
    print_response("Performance Dashboard", response)
    return response.json() if response.status_code == 200 else None


# ==================== MAIN EXECUTION ====================

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("PHASE 4: PERFORMANCE TRACKING API EXAMPLES")
    print("="*60)
    print("\nNOTE: Update AUTH_TOKEN variable with a valid JWT token")
    print("Get token by logging in: POST /api/auth/login")
    print()
    
    # Uncomment the examples you want to run:
    
    # 1. Track different performance types
    # example_track_listening()
    # example_track_speaking()
    # example_track_reading()
    # example_track_writing()
    # example_track_real_world()
    
    # 2. Get analytics and insights
    # example_get_trajectory()
    # example_get_patterns()
    # example_predict_mastery()
    
    # 3. Get performance history and dashboard
    # example_get_history()
    # example_get_dashboard()
    
    print("\n" + "="*60)
    print("To run examples, uncomment the function calls in main()")
    print("and update AUTH_TOKEN with a valid JWT token")
    print("="*60)


if __name__ == "__main__":
    main()
