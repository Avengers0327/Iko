# Iko 🤖

> *"I have a fully functioning personality chip, a rich inner life, and very strong opinions about color-blocking."*

A conversational AI robot personality based on **Iko** from Marissa Meyer's *The Lunar Chronicles*, running on a Raspberry Pi Zero. Powered by Groq's ultra-fast inference API and built with Python.

---

## What is this?

Iko is a chatbot — and eventually a physical robot — with a full personality: bubbly, fashion-obsessed, fiercely loyal, and dramatically expressive. She remembers your conversations between sessions using a local SQLite database, and she runs fast enough for real-time interaction thanks to Groq's LPU hardware.

This project is the backend brain of a physical robot build in progress.

---

## Features

- 🧠 **Persistent memory** — Iko remembers past conversations via SQLite, across sessions
- ⚡ **Fast inference** — Groq API delivers responses in ~200–400ms
- 🎭 **Full character adherence** — detailed system prompt keeps Iko in character
- 🤖 **Pi Zero ready** — lightweight stack, no heavy dependencies
- 💬 **Natural conversation** — history is passed in full context each turn

---

## Stack

| Thing | What it does |
|---|---|
| Python | Core language |
| Groq API | LLM inference (`llama-3.3-70b-versatile`) |
| SQLite | Persistent conversation memory |
| python-dotenv | API key management |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/iko.git
cd iko
```

**2. Install dependencies**
```bash
pip install groq python-dotenv
```

**3. Create a `.env` file**
```
GROQ_API_KEY=your_key_here
```
Get a free API key at [console.groq.com](https://console.groq.com)

**4. Run**
```bash
python iko.py
```

---

## File structure

```
iko/
├── iko.py        
├── history.db      
├── .env            
├── .gitignore
└── README.md
```

---

## .gitignore

Make sure your `.gitignore` includes:
```
.env
history.db
```

---

## Roadmap

- [x] Conversational AI with Iko's personality
- [x] Persistent memory across sessions (SQLite)
- [ ] Speech-to-text input (Pi Zero mic)
- [ ] Text-to-speech output
- [ ] Physical robot body integration
- [ ] Sensor awareness (camera, distance, etc.)

---

## Based on

Iko is a character from [*The Lunar Chronicles*](https://www.goodreads.com/series/69750-the-lunar-chronicles) by Marissa Meyer. This is a fan project — no affiliation with the author or publisher.

---

*Built with way too much enthusiasm and a healthy respect for android rights.*
