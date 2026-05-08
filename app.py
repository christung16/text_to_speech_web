import os
import uuid
import requests
from flask import Flask, render_template, request, url_for
from bs4 import BeautifulSoup
from gtts import gTTS
import shutil

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Ensure the audio directory exists
AUDIO_DIR = os.path.join(app.root_path, 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

def get_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        element.decompose()
    content = soup.find('article') or soup.find('main') or soup.body
    return " ".join(content.get_text(separator=" ").split())

@app.route("/", methods=["GET", "POST"])
def index():
    # Simple way to clear old audio files on every fresh visit
    if len(os.listdir(AUDIO_DIR)) > 50:  # If more than 50 files exist
        for f in os.listdir(AUDIO_DIR):
            os.remove(os.path.join(AUDIO_DIR, f))

    message, audio_url, url, lang = None, None, "", "en"

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        lang = request.form.get("lang", "en")
        try:
            text = get_text_from_url(url)[:500]
            if not text:
                message = "Could not find readable text."
            else:
                filename = f"{uuid.uuid4()}.mp3"
                filepath = os.path.join(AUDIO_DIR, filename)
                tts = gTTS(text=text, lang=lang)
                tts.save(filepath)
                audio_url = url_for('static', filename=f'audio/{filename}')
        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message, audio_url=audio_url, url=url, lang=lang)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)