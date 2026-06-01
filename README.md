# Iko 🤖
> "I have a fully functioning personality chip, a rich inner life, and very strong opinions about color-blocking."

A conversational AI robot personality based on Iko from Marissa Meyer's *The Lunar Chronicles*, running on cheap hardware. Powered by Groq's ultra-fast inference API and built with Python.

## What is this?

Iko is a voice-first chatbot — and eventually a physical robot — with a full personality: bubbly, fashion-obsessed, fiercely loyal, and dramatically expressive. She listens, responds, and speaks out loud in real time. She remembers your conversations between sessions using a local SQLite database, runs fast enough for natural back-and-forth thanks to Groq's LPU hardware, and can be interrupted mid-sentence if you have something to say.

This project is the backend brain of a physical robot build in progress.

## Features

- 🧠 **Persistent memory** — Iko remembers past conversations via SQLite, across sessions
- ⚡ **Fast inference** — Groq API delivers responses in ~200–400ms
- 🎤 **Voice input** — speech-to-text via ElevenLabs Scribe
- 🔊 **Voice output** — text-to-speech via ElevenLabs with a custom Iko voice
- ✋ **Interruptible playback** — VAD-based interruption detection lets you cut her off mid-sentence
- 🎭 **Full character adherence** — detailed system prompt keeps Iko in character
- 🤖 **Low-end hardware ready** — lightweight stack, no heavy dependencies

## Stack

| Thing | What it does |
|---|---|
| Python | Core language |
| Groq API | LLM inference (`llama-3.3-70b-versatile`) |
| ElevenLabs | Speech-to-text (Scribe) + text-to-speech |
| webrtcvad | Voice activity detection for interruption |
| sounddevice / soundfile | Audio playback and recording |
| SQLite | Persistent conversation memory |
| python-dotenv | API key management |

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/iko.git
cd iko
```

### 2. Install dependencies
```bash
pip install groq python-dotenv elevenlabs sounddevice soundfile webrtcvad numpy
```

### 3. Create a `.env` file
```
GROQ_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

- Groq: free API key at [console.groq.com](https://console.groq.com)
- ElevenLabs: API key at [elevenlabs.io](https://elevenlabs.io)

### 4. Run
```bash
python main.py
```

## File structure

```
iko/
├── main.py         # Core Iko class — listen, think, speak
├── freq_test.py    # Audio frequency debug tool
├── history.db      # Persistent conversation memory (auto-created)
├── .env            # API keys (never commit this)
├── .gitignore
└── README.md
```

## .gitignore

Make sure your `.gitignore` includes:
```
.env
history.db
```

## Roadmap

- [x] Conversational AI with Iko's personality
- [x] Persistent memory across sessions (SQLite)
- [x] Speech-to-text input
- [x] Text-to-speech output
- [x] Interruptible playback with VAD
- [ ] Physical robot body integration
- [ ] Sensor awareness (camera, distance, etc.)

## Based on

Iko is a character from *The Lunar Chronicles* by Marissa Meyer. This is a fan project — no affiliation with the author or publisher.

Built with way too much enthusiasm and a healthy respect for android rights.
