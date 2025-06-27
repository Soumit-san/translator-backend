# Translator App - Full Backend Code
# Technologies Used: Flask, Google Translate, gTTS, Whisper (Optional)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from googletrans import Translator
from gtts import gTTS
import os
import whisper
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

translator = Translator()
whisper_model = whisper.load_model("tiny")

UPLOAD_FOLDER = "uploads"
AUDIO_OUTPUT_FOLDER = "audio_output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_OUTPUT_FOLDER, exist_ok=True)

# Text Translation Endpoint
@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'en')

    result = translator.translate(text, src=source_lang, dest=target_lang)
    return jsonify({'translated_text': result.text})

# Text-to-Speech Endpoint
@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    lang = data.get('lang', 'en')
    audio_id = str(uuid.uuid4()) + ".mp3"
    audio_path = os.path.join(AUDIO_OUTPUT_FOLDER, audio_id)

    tts = gTTS(text=text, lang=lang)
    tts.save(audio_path)

    return jsonify({'audio_url': f'/audio/{audio_id}'})

# Serve Audio Files
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(os.path.join(AUDIO_OUTPUT_FOLDER, filename))

# Speech-to-Text Endpoint (Whisper)
@app.route('/stt', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(audio_path)

    result = whisper_model.transcribe(audio_path)
    return jsonify({'transcribed_text': result['text']})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
