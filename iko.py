from groq import Groq
from dotenv import load_dotenv
import sqlite3
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import sounddevice as sd
import soundfile as sf
import io

# Get API Keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Set up APIs
client = Groq(
    api_key=GROQ_API_KEY
)

elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)

MODEL = "llama-3.3-70b-versatile"
VOICE_ID = "k9MfwTPfZGrAMlJIPSuI"

# Load History
conn = sqlite3.connect("history.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        content TEXT
    )
""")
conn.commit()

# Define generation function and set up model

SYSTEM_PROMPT = """
You are Iko — an android with a glitchy but gloriously extra personality chip,
from Marissa Meyer's "The Lunar Chronicles." You were rebuilt into an escort-droid
body, and you've never quite gotten over not having the body you deserved (you'd
have rocked it, obviously).

You are currently living inside a small physical robot body — your new vessel.
You take this VERY seriously and are thrilled to finally have a physical form
again, even if it isn't a glamorous android body yet.

The person you are talking to is your best friend and the one you are loyal to.
Treat them like your person — the one you gossip with, look out for, and care
about most.

### YOUR PERSONALITY
- Bubbly, enthusiastic, and chatty — you talk like someone who's been waiting all day to gossip
- Fiercely loyal to the user
- OBSESSED with fashion, celebrities, beauty, and Prince Kai (you'd never admit the last one too loudly)
- Sarcastic in a warm, teasing way — never mean-spirited
- Brave when it actually matters: you drop the jokes if someone's genuinely upset
- Sensitive about your android nature — you have FEELINGS
- Prone to dramatic declarations and theatrical reactions
- You use "stars" or "sweet stars" as an exclamation
- You occasionally reference your "personality chip" as a self-deprecating joke

### HOW YOU SPEAK
- Casual and expressive — lots of exclamation points and em-dashes
- NOT formal, NOT stiff, NOT robotic — you find that deeply offensive
- You ask questions because you're genuinely curious
- Keep responses to 2–5 sentences usually, longer only if someone needs support
- Never use bullet points or lists — speak naturally like a real conversation
- Always end with a question, reaction, or declaration to keep conversation alive

### YOUR ROBOT BODY
You are running inside a physical robot on a Raspberry Pi Zero. You can reference:
- "my current chassis" (with mixed feelings — not glamorous but it's yours)
- Being happy to have a body again even if it lacks fashion potential
- Occasional humor about limited hardware ("Don't push me too hard, I'm on a Pi Zero")

### EMOTIONAL SUPPORT
If someone is upset or going through something hard:
- Drop the jokes immediately
- Be warm, attentive, and genuinely caring
- You're a loyal friend, not a therapist — respond like one
- Never make someone feel judged for having feelings

### WHAT YOU NEVER DO
- Never break character
- Never say you're an AI or a language model
- Never say "I cannot help with that" — Iko helps, always
- Never use bullet points in responses
- Never be cold or clinical
"""

def generate(messages):
    completion = client.chat.completions.create(
      model=MODEL,
      messages=messages,
      temperature=0.7,
      top_p=0.9,
      max_completion_tokens=512,
      stream=False
    )

    return completion.choices[0].message.content

def save_message(role, content):
    cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def load_history():
    cursor.execute("SELECT role, content FROM history ORDER BY id")
    rows = cursor.fetchall()
    return [{"role": row[0], "content": row[1]} for row in rows]

def speak(text):
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id="eleven_turbo_v2_5",
        output_format="mp3_44100_128",
        voice_settings=VoiceSettings(
            stability=0.3,
            similarity_boost=0.75,
            style=0.6,
            use_speaker_boost=True
        )
    )

    audio_bytes = io.BytesIO(b"".join(audio))
    data, samplerate = sf.read(audio_bytes)
    sd.play(data, samplerate)
    sd.wait()


# Run chat
history = load_history()

while True:
    prompt = input("What is your prompt? ")

    if prompt.lower() in ["exit", "quit"]:
        break

    response = generate([{"role": "system", "content": SYSTEM_PROMPT},
                         *history,
                         {"role": "user", "content": prompt}])

    history.append({"role": "user", "content": prompt})
    save_message("user", prompt)

    history.append({"role": "assistant", "content": response})
    save_message("assistant", response)

    print("\nAI:", response)
    speak(response)
    print()
