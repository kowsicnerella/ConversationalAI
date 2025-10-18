"""
Centralized LLM Configuration
Handles all AI interactions with support for multiple providers and modalities
Currently uses Google Gemini, easily swappable to custom inference endpoints
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import json
import requests
from typing import Optional, Dict, List, Any, Union
from enum import Enum
from PIL import Image
import google.generativeai as genai
from config import Config


# Find .env directories up
env_path = Path(__file__).resolve().parents[3] / ".env"

# Load it
load_dotenv(dotenv_path=env_path)


class LLMProvider(Enum):
    """Supported LLM providers"""

    GEMINI = "gemini"
    OPENAI = "openai"
    CUSTOM = "custom"


class LLMModality(Enum):
    """Different AI modalities"""

    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class LLMConfig:
    """
    Centralized LLM configuration and interaction class
    Single point of modification for all AI model interactions
    """

    # Default provider (easily changeable)
    DEFAULT_PROVIDER = LLMProvider.CUSTOM  # Custom model with Gemini as fallback

    # Model configurations
    MODELS = {
        LLMProvider.GEMINI: {
            "text": "gemini-2.0-flash-exp",
            "vision": "gemini-2.0-flash-exp",
            "audio": "gemini-2.0-flash-exp",
            "multimodal": "gemini-2.0-flash-exp",
        },
        LLMProvider.OPENAI: {
            "text": "gpt-4",
            "vision": "gpt-4-vision-preview",
            "audio": "whisper-1",
            "multimodal": "gpt-4-vision-preview",
        },
        LLMProvider.CUSTOM: {
            "text": "sarvamai/sarvam-m",
            "vision": "custom-vision",
            "audio": "custom-audio",
            "multimodal": "custom-multimodal",
        },
    }

    # Custom endpoint URLs (for future use)
    CUSTOM_ENDPOINTS = {
        "text": os.getenv(
            "CUSTOM_TEXT_ENDPOINT", f'{os.getenv("VLLM_ENDPOINT")}/v1/chat/completions'
        ),
        "vision": os.getenv(
            "CUSTOM_VISION_ENDPOINT", "http://localhost:8000/v1/vision/analyze"
        ),
        "audio": os.getenv(
            "CUSTOM_AUDIO_ENDPOINT", "http://localhost:8000/v1/audio/transcribe"
        ),
        "speech": os.getenv(
            "CUSTOM_SPEECH_ENDPOINT", "http://localhost:8000/v1/audio/synthesize"
        ),
    }

    # Default generation parameters
    DEFAULT_PARAMS = {
        "temperature": 0.7,
        "max_completion_tokens": 2048,
        "top_p": 0.9,
        "top_k": 40,
        "stop_sequences": None,
    }

    # Initialize Gemini (current provider)
    @classmethod
    def _init_gemini(cls):
        """Initialize Google Gemini API"""
        if not hasattr(cls, "_gemini_initialized"):
            genai.configure(api_key=Config.GEMINI_API_KEY)
            cls._gemini_initialized = True

    # ==================== TEXT GENERATION ====================

    @classmethod
    def generate_text(
        cls,
        prompt: str,
        provider: LLMProvider = None,
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate text completion from prompt with automatic fallback

        Args:
            prompt: Input text prompt
            provider: LLM provider to use (default: CUSTOM with Gemini fallback)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: System instruction/context
            json_mode: Force JSON output format

        Returns:
            {
                'success': bool,
                'text': str,
                'model': str,
                'usage': dict,
                'error': str (if failed)
            }
        """
        provider = provider or cls.DEFAULT_PROVIDER
        temperature = (
            temperature
            if temperature is not None
            else cls.DEFAULT_PARAMS["temperature"]
        )
        max_tokens = max_tokens or cls.DEFAULT_PARAMS["max_completion_tokens"]

        try:
            if provider == LLMProvider.GEMINI:
                return cls._gemini_generate_text(
                    prompt, temperature, max_tokens, system_prompt, json_mode
                )
            elif provider == LLMProvider.CUSTOM:
                # Try custom first, fallback to Gemini on error
                try:
                    return cls._custom_generate_text(
                        prompt, temperature, max_tokens, system_prompt
                    )
                except Exception as custom_error:
                    print(f"Custom LLM failed: {custom_error}. Falling back to Gemini...")
                    return cls._gemini_generate_text(
                        prompt, temperature, max_tokens, system_prompt, json_mode
                    )
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider} not implemented yet",
                }

        except Exception as e:
            return {"success": False, "error": f"Text generation failed: {str(e)}"}

    @classmethod
    def _gemini_generate_text(
        cls,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: str = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """Generate text using Gemini API"""
        cls._init_gemini()

        model_name = cls.MODELS[LLMProvider.GEMINI]["text"]
        model = genai.GenerativeModel(model_name)

        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        if json_mode:
            full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting, no extra text."

        # Generate
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=cls.DEFAULT_PARAMS["top_p"],
                top_k=cls.DEFAULT_PARAMS["top_k"],
            ),
        )

        text = response.text.strip()

        # Clean JSON if needed
        if json_mode:
            text = cls._clean_json_response(text)

        return {
            "success": True,
            "text": text,
            "model": model_name,
            "usage": {
                "total_tokens": (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 0
                )
            },
        }

    @classmethod
    def _custom_generate_text(
        cls, prompt: str, temperature: float, max_tokens: int, system_prompt: str = None
    ) -> Dict[str, Any]:
        """Generate text using custom inference endpoint"""
        endpoint = cls.CUSTOM_ENDPOINTS["text"]
        
        # Check if endpoint is configured
        if not endpoint or endpoint == "None/v1/chat/completions" or "None" in endpoint:
            raise ValueError("Custom LLM endpoint not configured. Set VLLM_ENDPOINT in .env file.")

        # OpenAI-compatible API format
        payload = {
            "model": cls.MODELS[LLMProvider.CUSTOM]["text"],
            "skip_special_tokens": False,
            "add_special_tokens": True,
            "include_reasoning": True,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt or "You are a helpful AI assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }

        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        return {
            "success": True,
            "text": data["choices"][0]["message"]["content"],
            "model": data.get("model", "custom"),
            "usage": data.get("usage", {}),
        }

    # ==================== CHAT COMPLETION ====================

    @classmethod
    def chat_completion(
        cls,
        messages: List[Dict[str, str]],
        stream: bool,
        provider: LLMProvider = None,
        temperature: float = None,
        max_tokens: int = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Chat-style completion with conversation history and automatic fallback

        Args:
            messages: List of {'role': 'user/assistant/system', 'content': 'text'}
            stream: Whether to stream the response
            provider: LLM provider to use (default: CUSTOM with Gemini fallback)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Force JSON output

        Returns:
            {
                'success': bool,
                'message': str,
                'model': str,
                'usage': dict
            }
        """
        provider = provider or cls.DEFAULT_PROVIDER
        temperature = (
            temperature
            if temperature is not None
            else cls.DEFAULT_PARAMS["temperature"]
        )
        max_tokens = max_tokens or cls.DEFAULT_PARAMS["max_completion_tokens"]

        try:
            if provider == LLMProvider.GEMINI:
                return cls._gemini_chat_completion(
                    messages, temperature, max_tokens, json_mode
                )
            elif provider == LLMProvider.CUSTOM:
                # Try custom first, fallback to Gemini on error
                try:
                    return cls._custom_chat_completion(
                        messages, temperature, max_tokens, stream
                    )
                except Exception as custom_error:
                    print(f"Custom LLM chat failed: {custom_error}. Falling back to Gemini...")
                    return cls._gemini_chat_completion(
                        messages, temperature, max_tokens, json_mode
                    )
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider} not implemented yet",
                }

        except Exception as e:
            return {"success": False, "error": f"Chat completion failed: {str(e)}"}

    @classmethod
    def _gemini_chat_completion(
        cls,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """Chat completion using Gemini"""
        cls._init_gemini()

        model_name = cls.MODELS[LLMProvider.GEMINI]["text"]
        model = genai.GenerativeModel(model_name)

        # Convert messages to Gemini format
        chat = model.start_chat(history=[])

        # Add conversation history
        for msg in messages[:-1]:  # All except last
            role = "user" if msg["role"] in ["user", "system"] else "model"
            chat.history.append({"role": role, "parts": [msg["content"]]})

        # Send last message
        last_message = messages[-1]["content"]
        if json_mode:
            last_message += "\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting, no extra text."

        response = chat.send_message(
            last_message,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=cls.DEFAULT_PARAMS["top_p"],
                top_k=cls.DEFAULT_PARAMS["top_k"],
            ),
        )

        text = response.text.strip()
        if json_mode:
            text = cls._clean_json_response(text)

        return {
            "success": True,
            "message": text,
            "model": model_name,
            "usage": {
                "total_tokens": (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 0
                )
            },
        }

    @classmethod
    def _custom_chat_completion(
        cls,
        messages: List[Dict[str, str]],
        stream: bool,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Chat completion using custom endpoint"""
        endpoint = cls.CUSTOM_ENDPOINTS["text"]

        payload = {
            "model": cls.MODELS[LLMProvider.CUSTOM]["text"],
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }

        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        return {
            "success": True,
            "message": data["choices"][0]["message"]["content"],
            "model": data.get("model", "custom"),
            "usage": data.get("usage", {}),
        }

    # ==================== IMAGE ANALYSIS (VISION) ====================

    @classmethod
    def analyze_image(
        cls,
        image: Union[str, Image.Image],
        prompt: str,
        provider: LLMProvider = None,
        temperature: float = None,
        max_tokens: int = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze image with AI vision model and automatic fallback

        Args:
            image: PIL Image object or path to image file
            prompt: Text prompt describing what to analyze
            provider: LLM provider to use (default: CUSTOM with Gemini fallback)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Force JSON output

        Returns:
            {
                'success': bool,
                'analysis': str,
                'model': str,
                'usage': dict
            }
        """
        provider = provider or cls.DEFAULT_PROVIDER
        temperature = (
            temperature
            if temperature is not None
            else cls.DEFAULT_PARAMS["temperature"]
        )
        max_tokens = max_tokens or cls.DEFAULT_PARAMS["max_completion_tokens"]

        try:
            if provider == LLMProvider.GEMINI:
                return cls._gemini_analyze_image(
                    image, prompt, temperature, max_tokens, json_mode
                )
            elif provider == LLMProvider.CUSTOM:
                # Try custom first, fallback to Gemini on error
                try:
                    return cls._custom_analyze_image(image, prompt, temperature, max_tokens)
                except Exception as custom_error:
                    print(f"Custom vision failed: {custom_error}. Falling back to Gemini...")
                    return cls._gemini_analyze_image(
                        image, prompt, temperature, max_tokens, json_mode
                    )
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider} not implemented yet",
                }

        except Exception as e:
            return {"success": False, "error": f"Image analysis failed: {str(e)}"}

    @classmethod
    def _gemini_analyze_image(
        cls,
        image: Union[str, Image.Image],
        prompt: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """Analyze image using Gemini Vision"""
        cls._init_gemini()

        model_name = cls.MODELS[LLMProvider.GEMINI]["vision"]
        model = genai.GenerativeModel(model_name)

        # Load image if path provided
        if isinstance(image, str):
            image = Image.open(image)

        # Add JSON instruction if needed
        if json_mode:
            prompt += "\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting, no extra text."

        # Generate
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=cls.DEFAULT_PARAMS["top_p"],
                top_k=cls.DEFAULT_PARAMS["top_k"],
            ),
        )

        text = response.text.strip()
        if json_mode:
            text = cls._clean_json_response(text)

        return {
            "success": True,
            "analysis": text,
            "model": model_name,
            "usage": {
                "total_tokens": (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 0
                )
            },
        }

    @classmethod
    def _custom_analyze_image(
        cls,
        image: Union[str, Image.Image],
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Analyze image using custom vision endpoint"""
        endpoint = cls.CUSTOM_ENDPOINTS["vision"]

        # Convert image to base64 if needed
        import base64
        import io

        if isinstance(image, str):
            image = Image.open(image)

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        payload = {
            "model": cls.MODELS[LLMProvider.CUSTOM]["vision"],
            "image": img_base64,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        return {
            "success": True,
            "analysis": data.get("analysis", data.get("text", "")),
            "model": data.get("model", "custom-vision"),
            "usage": data.get("usage", {}),
        }

    # ==================== AUDIO PROCESSING ====================

    @classmethod
    def transcribe_audio(
        cls, audio_file: str, provider: LLMProvider = None, language: str = "en"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text (Speech-to-Text)

        Args:
            audio_file: Path to audio file
            provider: LLM provider to use
            language: Language code (e.g., 'en', 'te')

        Returns:
            {
                'success': bool,
                'text': str,
                'language': str,
                'duration': float,
                'model': str
            }
        """
        provider = provider or cls.DEFAULT_PROVIDER

        try:
            if provider == LLMProvider.GEMINI:
                return cls._gemini_transcribe_audio(audio_file, language)
            elif provider == LLMProvider.CUSTOM:
                return cls._custom_transcribe_audio(audio_file, language)
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider} not implemented yet",
                }

        except Exception as e:
            return {"success": False, "error": f"Audio transcription failed: {str(e)}"}

    @classmethod
    def _gemini_transcribe_audio(cls, audio_file: str, language: str) -> Dict[str, Any]:
        """Transcribe audio using Gemini (multimodal)"""
        cls._init_gemini()

        # Gemini can process audio files directly
        model_name = cls.MODELS[LLMProvider.GEMINI]["audio"]
        model = genai.GenerativeModel(model_name)

        # Upload audio file
        audio = genai.upload_file(audio_file)

        prompt = f"Transcribe this audio in {language} language. Return ONLY the transcribed text, no additional commentary."

        response = model.generate_content([prompt, audio])

        return {
            "success": True,
            "text": response.text.strip(),
            "language": language,
            "model": model_name,
        }

    @classmethod
    def _custom_transcribe_audio(cls, audio_file: str, language: str) -> Dict[str, Any]:
        """Transcribe audio using custom endpoint"""
        endpoint = cls.CUSTOM_ENDPOINTS["audio"]

        with open(audio_file, "rb") as f:
            files = {"audio": f}
            data = {"language": language}

            response = requests.post(endpoint, files=files, data=data, timeout=120)
            response.raise_for_status()

        result = response.json()
        return {
            "success": True,
            "text": result.get("text", ""),
            "language": language,
            "model": result.get("model", "custom-audio"),
        }

    @classmethod
    def generate_speech(
        cls,
        text: str,
        provider: LLMProvider = None,
        language: str = "en",
        voice: str = "default",
    ) -> Dict[str, Any]:
        """
        Generate speech from text (Text-to-Speech)

        Args:
            text: Text to convert to speech
            provider: LLM provider to use
            language: Language code
            voice: Voice identifier

        Returns:
            {
                'success': bool,
                'audio_data': bytes,
                'format': str,
                'model': str
            }
        """
        provider = provider or cls.DEFAULT_PROVIDER

        try:
            if provider == LLMProvider.CUSTOM:
                return cls._custom_generate_speech(text, language, voice)
            else:
                return {
                    "success": False,
                    "error": f"TTS not implemented for {provider}",
                }

        except Exception as e:
            return {"success": False, "error": f"Speech generation failed: {str(e)}"}

    @classmethod
    def _custom_generate_speech(
        cls, text: str, language: str, voice: str
    ) -> Dict[str, Any]:
        """Generate speech using custom TTS endpoint"""
        endpoint = cls.CUSTOM_ENDPOINTS["speech"]

        payload = {"text": text, "language": language, "voice": voice}

        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()

        return {
            "success": True,
            "audio_data": response.content,
            "format": "wav",
            "model": "custom-tts",
        }

    # ==================== UTILITY FUNCTIONS ====================

    @classmethod
    def _clean_json_response(cls, text: str) -> str:
        """Clean JSON response from markdown formatting"""
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    @classmethod
    def set_provider(cls, provider: LLMProvider):
        """Change default provider globally"""
        cls.DEFAULT_PROVIDER = provider

    @classmethod
    def set_custom_endpoint(cls, modality: str, endpoint: str):
        """Set custom endpoint URL for specific modality"""
        if modality in cls.CUSTOM_ENDPOINTS:
            cls.CUSTOM_ENDPOINTS[modality] = endpoint

    @classmethod
    def get_available_models(cls, provider: LLMProvider = None) -> Dict[str, str]:
        """Get available models for provider"""
        provider = provider or cls.DEFAULT_PROVIDER
        return cls.MODELS.get(provider, {})


# Convenience functions for quick access
def generate_text(prompt: str, **kwargs) -> str:
    """Quick text generation - returns text directly"""
    result = LLMConfig.generate_text(prompt, **kwargs)
    return result.get("text", "") if result.get("success") else ""


def analyze_image(image, prompt: str, **kwargs) -> str:
    """Quick image analysis - returns analysis directly"""
    result = LLMConfig.analyze_image(image, prompt, **kwargs)
    return result.get("analysis", "") if result.get("success") else ""


def chat(messages: List[Dict[str, str]], stream: bool = True, **kwargs) -> str:
    """Quick chat completion - returns message directly"""
    result = LLMConfig.chat_completion(messages, stream, **kwargs)
    return result.get("message", "") if result.get("success") else ""
