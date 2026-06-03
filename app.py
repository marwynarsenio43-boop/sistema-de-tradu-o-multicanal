import os
import tempfile
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_AUDIO = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'}
ALLOWED_TEXT  = {'txt', 'pdf', 'docx'}

LANGUAGES = {
    "Português": "pt",
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "Italiano": "it",
    "中文 (Chinês)": "zh",
    "日本語 (Japonês)": "ja",
    "العربية (Árabe)": "ar",
    "Русский (Russo)": "ru",
    "Kiswahili": "sw",
    "Zulu": "zu",
    "Yoruba": "yo",
    "Hausa": "ha",
    "Afrikaans": "af",
}

def get_client():
    api_key = request.headers.get('X-API-Key') or request.json.get('api_key') if request.is_json else request.form.get('api_key')
    if not api_key:
        return None, "Chave API não fornecida."
    return OpenAI(api_key=api_key), None

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def translate_text(client, text, target_language, source_language="auto"):
    lang_name = next((k for k, v in LANGUAGES.items() if v == target_language), target_language)
    src_note = f"O texto está em {source_language}. " if source_language != "auto" else ""
    
    prompt = f"""{src_note}Traduz o seguinte texto para {lang_name}.
Devolve APENAS o texto traduzido, sem explicações, notas ou marcações extra.

Texto a traduzir:
{text}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "És um tradutor profissional. Traduz com precisão preservando o tom, formatação e contexto original."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def transcribe_audio(client, audio_file_path, source_language=None):
    with open(audio_file_path, 'rb') as f:
        kwargs = {"model": "whisper-1", "file": f, "response_format": "text"}
        if source_language and source_language != "auto":
            kwargs["language"] = source_language
        result = client.audio.transcriptions.create(**kwargs)
    return result

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate/text', methods=['POST'])
def translate_text_route():
    try:
        data = request.json
        api_key = data.get('api_key', '').strip()
        if not api_key:
            return jsonify({'error': 'Chave API é obrigatória.'}), 400

        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Texto não pode estar vazio.'}), 400

        target_lang = data.get('target_language', 'pt')
        source_lang = data.get('source_language', 'auto')

        client = OpenAI(api_key=api_key)
        translated = translate_text(client, text, target_lang, source_lang)
        return jsonify({'success': True, 'original': text, 'translated': translated, 'target_language': target_lang})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/translate/audio', methods=['POST'])
def translate_audio_route():
    try:
        api_key = request.form.get('api_key', '').strip()
        if not api_key:
            return jsonify({'error': 'Chave API é obrigatória.'}), 400

        if 'audio' not in request.files:
            return jsonify({'error': 'Nenhum ficheiro de áudio enviado.'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'Nome de ficheiro inválido.'}), 400

        if not allowed_file(audio_file.filename, ALLOWED_AUDIO):
            return jsonify({'error': f'Formato não suportado. Use: {", ".join(ALLOWED_AUDIO)}'}), 400

        target_lang    = request.form.get('target_language', 'pt')
        source_lang    = request.form.get('source_language', 'auto')
        translate_only = request.form.get('translate', 'true').lower() == 'true'

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(audio_file.filename)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1], dir=app.config['UPLOAD_FOLDER']) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            client = OpenAI(api_key=api_key)
            transcribed = transcribe_audio(client, tmp_path, source_lang if source_lang != 'auto' else None)

            result = {'success': True, 'transcription': transcribed}

            if translate_only:
                translated = translate_text(client, transcribed, target_lang, source_lang)
                result['translated']       = translated
                result['target_language']  = target_lang
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/languages')
def get_languages():
    return jsonify(LANGUAGES)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
