# 🌐 TranslateX — Sistema de Tradução Multicanal

Aplicação web para tradução de texto e áudio usando a **API da OpenAI** (Whisper + GPT-4o mini).

---

## ✨ Funcionalidades

| Funcionalidade | Detalhe |
|---|---|
| 📝 Tradução de texto | Cola ou escreve qualquer texto para traduzir |
| 🎙️ Transcrição de áudio | Converte áudio em texto via Whisper |
| 🌍 +15 idiomas | PT, EN, ES, FR, DE, IT, ZH, JA, AR, RU, SW, ZU, YO, HA, AF |
| 🔍 Detecção automática | Whisper e GPT detectam o idioma de origem |
| 📋 Copiar resultado | Copia a tradução com um clique |
| 📱 Responsivo | Funciona em mobile e desktop |

---

## 🚀 Como executar localmente

### Pré-requisitos
- Python 3.10+
- Conta OpenAI com API Key → [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU_USERNAME/sistema-traducao.git
cd sistema-traducao

# 2. Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar
python app.py
```

Abre o browser em `http://localhost:5000`

---

## 📁 Estrutura do Projecto

```
sistema-traducao/
├── app.py              # Backend Flask + endpoints API
├── requirements.txt    # Dependências Python
├── Procfile            # Para deploy no Render/Railway
├── render.yaml         # Configuração Render
├── templates/
│   └── index.html      # Interface web (HTML + CSS + JS)
└── uploads/            # Pasta temporária (ignorada pelo Git)
```

---

## 🌐 Deploy no Render (Grátis)

1. Faz push do código para o GitHub
2. Vai a [render.com](https://render.com) → **New Web Service**
3. Liga ao teu repositório GitHub
4. As configurações são detectadas automaticamente via `render.yaml`
5. Clica **Deploy** — o processo demora ~2 minutos

> ⚠️ **A API Key é introduzida pelo utilizador na interface** — não precisas de variáveis de ambiente.

---

## 🔊 Formatos de áudio suportados

`MP3` · `WAV` · `OGG` · `FLAC` · `M4A` · `WEBM` · `MP4` · `MPEG`

Tamanho máximo: **25 MB** (limite do Whisper API)

---

## 💰 Custo estimado (OpenAI)

| Operação | Modelo | Custo aproximado |
|---|---|---|
| Tradução de texto | GPT-4o mini | ~$0.0001 por 1000 palavras |
| Transcrição de áudio | Whisper | $0.006 por minuto |
| Transcrição + Tradução | Whisper + GPT-4o mini | < $0.01 por operação típica |

**Praticamente gratuito** para uso académico e pessoal.

---

## 🛠️ API Endpoints

### `POST /translate/text`
```json
{
  "api_key": "sk-...",
  "text": "Hello world",
  "source_language": "auto",
  "target_language": "pt"
}
```

### `POST /translate/audio`
Form-data:
- `api_key` — OpenAI API key
- `audio` — ficheiro de áudio
- `source_language` — código do idioma ou `auto`
- `target_language` — código do idioma destino
- `translate` — `true` ou `false`
