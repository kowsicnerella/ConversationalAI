
# !pip install -U transformers gtts soundfile langdetect torch

import re
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from gtts import gTTS
from langdetect import detect

ASR_MODEL = "openai/whisper-small"
# LLM_MODEL = "Qwen/Qwen3-0.6B"
# LLM_MODEL="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LLM_MODEL="ibm-granite/granite-4.0-micro"

# -----------------------------
# Utilities
# -----------------------------
def mask_pii(text: str) -> str:
    text = re.sub(r'\b\d{10}\b', '[PHONE_NUMBER]', text)
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[EMAIL]', text)
    return text

def clean_output(output_text: str) -> str:
    return (re.sub(r'<think>.*?</think>', '', output_text, flags=re.DOTALL).strip()).split('#')[0]

def build_prompt(user_text: str, lang_code: str) -> str:
    system_instruction = f"""
You are a helpful multilingual assistant.

Reply strictly in the same language as the user's input.

Keep replies short, natural, and friendly.

Do NOT include any special characters, punctuation, or formatting like ###, quotes, or emojis.

Only output the text that should be spoken. Nothing else.

Make sentences crisp and clear for text-to-speech output.

Examples:

Hindi:
User: "आप कैसे हैं"
Assistant: "मैं ठीक हूँ आप बताइए"

Telugu:
User: "మీరు ఎలా ఉన్నారు"
Assistant: "నేను బాగున్నాను మీరు చెప్పండి"

English:
User: "How are you"
Assistant: "I'm good how about you"

Respond only with the text to speak, nothing else.
"""
    return f"### System:\n{system_instruction.strip()}\n\n### User:\n{user_text}\n\n### Assistant:\n"

# -----------------------------
# Load Models
# -----------------------------
print("Loading ASR...")
asr_pipe = pipeline("automatic-speech-recognition", model=ASR_MODEL)

print("Loading  model locally...")
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, trust_remote_code=True, device_map="auto")

gen_pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

# -----------------------------
# Main Function
# -----------------------------
def audio_to_llm_response(audio_file_path: str, output_tts_file="reply.mp3"):
    # Step 1: ASR
    transcription = asr_pipe(audio_file_path)["text"]
    safe_text = mask_pii(transcription)

    # Step 2: Language detection
    try:
        lang_code = detect(safe_text)
    except:
        lang_code = "en"

    # Step 3: Build prompt with examples
    prompt = build_prompt(safe_text, lang_code)

    # Step 4: Generate LLM response
    output = gen_pipe(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)[0]["generated_text"]
    llm_reply = clean_output(output[len(prompt):])

    # Step 5: Convert only LLM reply to speech
    try:
        tts = gTTS(text=llm_reply, lang=lang_code)
        tts.save(output_tts_file)
        print(f"Audio reply saved as {output_tts_file}")
    except Exception as e:
        print(f"TTS failed for language {lang_code}: {e}")

    # Step 6: Return only the LLM reply text
    return llm_reply
if __name__ == "__main__":
    audio_file = "/content/generated-audio.mp3"  # Replace with your audio file path
    reply_text = audio_to_llm_response(audio_file, "reply.mp3")
    print("LLM Reply:", reply_text)

