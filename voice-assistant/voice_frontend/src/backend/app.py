from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from asr_pipeline import audio_to_llm_response

app = Flask(__name__)
CORS(app)

@app.route("/process-audio", methods=["POST"])
def process_audio():
    try:
        audio = request.files["audio"]
        audio_path = "temp_audio.wav"
        audio.save(audio_path)

        reply_text = audio_to_llm_response(audio_path, "reply.mp3")
        return jsonify({"reply_text": reply_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-audio", methods=["GET"])
def get_audio():
    return send_file("reply.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
