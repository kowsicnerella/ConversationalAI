import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API key
# It's recommended to use environment variables for API keys
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def _extract_json_from_response(text):
    """
    Extracts a JSON object from a string response, handling markdown code blocks.
    """
    # Match the JSON content inside a markdown code block
    match = re.search(r"```json\n({.*?})\n```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # If no markdown block, assume the whole string is a JSON object
        json_str = text

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Handle cases where the JSON is malformed or the response is not JSON
        # You might want to add more robust error handling or logging here
        return {"error": "Failed to parse JSON from response.", "raw_response": text}


class ActivityGeneratorService:
    """
    A service class to generate various learning activities using the Gemini API.
    """

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_quiz(self, topic, level="beginner"):
        """
        Generates a multiple-choice quiz for Telugu speakers learning English.
        """
        prompt = f"""
        Generate a 5-question multiple-choice quiz for a Telugu speaker learning English at '{level}' level on the topic of '{topic}'.
        The questions should be in English and test English vocabulary, grammar, or comprehension.
        Provide Telugu translations or explanations where helpful for better understanding.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object should have a single key "questions", which is a list of question objects.
        Each question object must have the following keys:
        - "question_text": The question in English.
        - "question_telugu": Optional Telugu translation/explanation of the question.
        - "options": A list of 4 English strings representing the possible answers.
        - "correct_answer": The string from the "options" list that is the correct answer.
        - "explanation": Brief explanation in English with Telugu translation if needed.

        Example format:
        ```json
        {{
            "questions": [
                {{
                    "question_text": "What does 'apple' mean?",
                    "question_telugu": "'apple' అంటే ఏమిటి?",
                    "options": ["A fruit", "A vegetable", "A color", "An animal"],
                    "correct_answer": "A fruit",
                    "explanation": "Apple is a fruit. Telugu: యాపిల్ ఒక పండు."
                }}
            ]
        }}
        ```
        """
        response = self.model.generate_content(prompt)
        return _extract_json_from_response(response.text)

    def generate_flashcards(self, topic, level="beginner"):
        """
        Generates English flashcards with Telugu translations for Telugu speakers.
        """
        prompt = f"""
        Generate a set of 10 English flashcards for a Telugu speaker at '{level}' level on the topic of '{topic}'.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object should have a single key "flashcards", which is a list of flashcard objects.
        Each flashcard object must have "front" (English word/phrase) and "back" (Telugu translation).

        Example format:
        ```json
        {{
            "flashcards": [
                {{
                    "front": "Hello",
                    "back": "హలో / నమస్కారం"
                }},
                {{
                    "front": "Goodbye",
                    "back": "వీడ్కోలు"
                }}
            ]
        }}
        ```
        """
        response = self.model.generate_content(prompt)
        return _extract_json_from_response(response.text)

    def generate_general_chat_response(self, message_history, user_message):
        """
        Generates a response for English learning chat for Telugu speakers.
        """
        system_prompt = "You are a friendly English tutor helping Telugu speakers learn English. Respond in English but provide Telugu translations when helpful. Keep responses simple and encouraging."
        # The message history should be formatted correctly for the API
        conversation = [system_prompt] + message_history + [user_message]
        response = self.model.generate_content(conversation)
        return response.text

    def generate_text_reading(self, topic, level="beginner"):
        """
        Generates English reading practice for Telugu speakers.
        """
        prompt = f"""
        Write a short paragraph (approx. 100 words) in English for a Telugu speaker at '{level}' level about '{topic}'.
        The paragraph should introduce 5 new English vocabulary words.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have two keys:
        - "reading_text": The full paragraph in English.
        - "vocabulary": A list of objects, where each object has "word" (the new English word) and "telugu_translation" (its Telugu meaning).

        Example format:
        ```json
        {{
            "reading_text": "...",
            "vocabulary": [
                {{
                    "word": "beautiful",
                    "telugu_translation": "అందమైన"
                }}
            ]
        }}
        ```
        """
        response = self.model.generate_content(prompt)
        return _extract_json_from_response(response.text)

    def generate_writing_practice_prompt(self, topic, level="beginner"):
        """
        Generates English writing practice prompts for Telugu speakers.
        """
        prompt = f"""
        Create a writing prompt for a Telugu speaker learning English at '{level}' level. The prompt should be about '{topic}'.
        Ask the user to write at least 5 sentences in English.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have two keys:
        - "prompt": The writing prompt in English.
        - "prompt_telugu": Telugu translation of the prompt for better understanding.

        Example format:
        ```json
        {{
            "prompt": "Describe your daily routine in English.",
            "prompt_telugu": "మీ రోజువారీ క్రమం కురిత్తే ఇంగ్లీష్ లో వర్ణించండి."
        }}
        ```
        """
        response = self.model.generate_content(prompt)
        return _extract_json_from_response(response.text)

    def generate_role_playing_scenario(self, topic, level="beginner"):
        """
        Generates English role-playing scenarios for Telugu speakers.
        """
        prompt = f"""
        Create a role-playing scenario for a Telugu speaker learning English at '{level}' level where the user needs to '{topic}'.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have the following keys:
        - "setting": A brief description of the scene in English.
        - "setting_telugu": Telugu translation of the setting.
        - "user_goal": What the user needs to accomplish in English.
        - "user_goal_telugu": Telugu translation of the goal.
        - "initial_line": The first line from the other character in English.

        Example format:
        ```json
        {{
            "setting": "At a local grocery store.",
            "setting_telugu": "కిరాణా దుకానం లో",
            "user_goal": "Buy fruits and vegetables.",
            "user_goal_telugu": "పండ్లు మరియు కూరగాయలు కొనడం",
            "initial_line": "Good morning! How can I help you today?"
        }}
        ```
        """
        response = self.model.generate_content(prompt)
        return _extract_json_from_response(response.text)

    def analyze_image_for_learning(self, image):
        """
        Analyzes an image for English learning activities for Telugu speakers.
        """
        prompt = f"""
        This user is a Telugu speaker learning English. Identify the main object in this image.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have the following keys:
        - "object_name_english": The name of the object in English.
        - "object_name_telugu": The Telugu translation of the object's name.
        - "sample_sentence": A simple sentence in English using the object's name.
        - "sentence_telugu": Telugu translation of the sample sentence.

        Example format:
        ```json
        {{
            "object_name_english": "apple",
            "object_name_telugu": "పెప్పండు",
            "sample_sentence": "I eat an apple every day.",
            "sentence_telugu": "నేను ప్రతి రోజు ఒక ఆపిల్ తిన్నడి."
        }}
        ```
        """
        response = self.vision_model.generate_content([prompt, image])
        return _extract_json_from_response(response.text)

    def get_feedback_on_writing(self, user_writing):
        """
        Provides structured feedback on English writing for Telugu speakers.
        """
        prompt = f"""
        The user is a Telugu speaker practicing English writing. Here is their writing: '{user_writing}'.
        Review it for grammatical errors and suggest improvements.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have three keys:
        - "corrected_text": The full text with corrections applied.
        - "errors": A list of error objects, where each object has "original_phrase", "correction", and "explanation".
        - "encouragement": A positive message in both English and Telugu to motivate the learner.

        Example format:
        ```json
        {{
            "corrected_text": "I go to school every day.",
            "errors": [
                {{
                    "original_phrase": "I goes to school",
                    "correction": "I go to school",
                    "explanation": "Use 'go' not 'goes' with 'I'. Telugu: 'నేను' తో 'go' వాడాలి, 'goes' కాదు."
                }}
            ],
            "encouragement": "Great effort! Keep practicing! Telugu: బాగా రాశారు! అభ్యసించడం కొనసాగించండి!"
        }}
        ```
        """
        response = self.model.generate_content(prompt)
        return _extract_json_from_response(response.text)

    def evaluate_activity_submission(self, activity_content, user_answers, activity_type):
        """
        Evaluate user's submitted answers for an activity and provide feedback.
        
        Args:
            activity_content (dict): The original activity content with questions/tasks
            user_answers (dict): User's responses to the activity
            activity_type (str): Type of activity (quiz, flashcard, etc.)
        
        Returns:
            dict: Evaluation results with score, feedback, and explanations
        """
        prompt = f"""
        Evaluate the user's answers for a Telugu-English learning activity.
        
        Activity Type: {activity_type}
        Activity Content: {json.dumps(activity_content, indent=2)}
        User Answers: {json.dumps(user_answers, indent=2)}
        
        Please evaluate the answers and provide:
        1. Score achieved (number correct)
        2. Maximum possible score
        3. Detailed feedback for each answer
        4. Encouragement in both English and Telugu
        5. Suggestions for improvement
        
        Return the response in JSON format:
        ```json
        {{
            "score": 4,
            "max_score": 5,
            "feedback": {{
                "question_1": {{
                    "correct": true,
                    "user_answer": "book",
                    "correct_answer": "book", 
                    "explanation": "Correct! Telugu: సరైనది!"
                }},
                "question_2": {{
                    "correct": false,
                    "user_answer": "goes",
                    "correct_answer": "go",
                    "explanation": "Incorrect. Use 'go' with 'I'. Telugu: 'నేను' తో 'go' వాడాలి."
                }}
            }},
            "overall_feedback": "Good job! You got 4 out of 5 correct.",
            "telugu_feedback": "బాగుంది! మీరు 5లో 4 సరిగా చేశారు.",
            "suggestions": [
                "Practice subject-verb agreement",
                "Review basic verb forms"
            ],
            "encouragement": "Keep practicing! You're making great progress!",
            "telugu_encouragement": "అభ్యసించడం కొనసాగించండి! మీరు బాగా పురోగతి సాధిస్తున్నారు!"
        }}
        ```
        """
        
        try:
            response = self.model.generate_content(prompt)
            evaluation_result = _extract_json_from_response(response.text)
            
            # Ensure required fields exist
            if 'score' not in evaluation_result:
                evaluation_result['score'] = 0
            if 'max_score' not in evaluation_result:
                evaluation_result['max_score'] = len(user_answers) if user_answers else 1
            if 'feedback' not in evaluation_result:
                evaluation_result['feedback'] = {}
                
            return evaluation_result
            
        except Exception as e:
            # Fallback evaluation if AI fails
            return {
                'score': 0,
                'max_score': len(user_answers) if user_answers else 1,
                'feedback': {},
                'overall_feedback': 'Unable to evaluate at this time. Please try again.',
                'telugu_feedback': 'ప్రస్తుతం మూల్యాంకనం చేయలేకపోతున్నాము. దయచేసి మళ్లీ ప్రయత్నించండి.',
                'error': str(e)
            }
