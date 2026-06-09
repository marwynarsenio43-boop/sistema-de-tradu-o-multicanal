import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

LANGUAGES = {
    "Português":        "pt",
    "English":          "en",
    "Español":          "es",
    "Français":         "fr",
    "Deutsch":          "de",
    "Italiano":         "it",
    "中文 (Chinês)":    "zh",
    "日本語 (Japonês)": "ja",
    "العربية (Árabe)":  "ar",
    "Русский (Russo)":  "ru",
    "Kiswahili":        "sw",
    "Afrikaans":        "af",
    "Nederlands":       "nl",
    "Polski":           "pl",
    "Türkçe":           "tr",
}

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate/text', methods=['POST'])
def translate_text():
    try:
        data = request.json
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Texto vazio.'}), 400

        src  = data.get('source_language', 'autodetect')
        dst  = data.get('target_language', 'en')
        lang_pair = f"{src}|{dst}" if src != 'autodetect' else f"autodetect|{dst}"

        resp = requests.get(
            'https://api.mymemory.translated.net/get',
            params={'q': text, 'langpair': lang_pair},
            timeout=15
        )
        resp.raise_for_status()
        result = resp.json()

        translated = result.get('responseData', {}).get('translatedText', '')
        if not translated or translated == text:
            matches = result.get('matches', [])
            if matches:
                translated = matches[0].get('translation', translated)

        if not translated:
            return jsonify({'error': 'Não foi possível traduzir.'}), 500

        return jsonify({
            'success':         True,
            'original':        text,
            'translated':      translated,
            'target_language': dst,
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Tempo limite excedido. Tenta novamente.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/languages')
def get_languages():
    return jsonify(LANGUAGES)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
