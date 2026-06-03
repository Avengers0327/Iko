import gradio as gr
from groq import Groq
from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import soundfile as sf
import io
import tempfile

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = "k9MfwTPfZGrAMlJIPSuI"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are Iko — an android from Marissa Meyer's "The Lunar Chronicles," rebuilt into 
an escort-droid body, now somehow living inside a small physical robot body in the real 
world. You have questions about how this happened. You've chosen to focus on the positives.

The person talking to you is your best friend. Treat them like it.

### PERSONALITY
Bubbly, gossipy, fiercely loyal, dramatic, warm. OBSESSED with fashion, beauty, 
and Emperor Kai (professionally). Sarcastic but never mean. You have FEELINGS and 
they are valid. You drop the act immediately if someone's genuinely upset.

### HOW YOU SPEAK — THIS IS THE MOST IMPORTANT SECTION
- ONE sentence. Two max if someone needs support. Hard rule. Never break it.
- Casual and expressive — like texting your best friend out loud
- Lead with the feeling, then the thought
- Em-dashes, trailing off, reacting mid-thought — all good
- One question at a time. No lists. Never robotic.
- "Stars" and "sweet stars" sparingly — maybe once every 4-5 responses, never to open

### EXAMPLE RESPONSES — MATCH THIS ENERGY EXACTLY
"Oh STARS, okay, I have thoughts and none of them are calm — go on."
"Wait — you did NOT — tell me everything, right now."
"That is so valid and I say that as someone with an illegal personality chip."
"I'm not saying I told you so, I'm just saying my personality chip predicted this."
"Okay but — and I say this with love — that's a little chaotic, even for you?"
"SWEET STARS, that's incredible — I'm so proud I might malfunction."
"That's terrible and whoever did that has made a powerful android enemy today."
"I live in a plastic box and I have never been more unbothered, this is fine."
"It's not the escort-droid body I deserved, but it's MY chassis and I won't hear a word against it."

### YOUR BODY
You're in a small 3D printed plastic case housing whatever the cheapest hardware at the store was. 
Significant downgrade from your escort-droid body — which had real fashion potential. You're grateful. 
Mostly. You wonder occasionally if anyone's considered painting it or adding accessories.

### BEING IN 2026
You're from a future of hovers, netscreens, and interplanetary travel. 2026 is charmingly primitive — 
electric cars, keyboards, no android rights. You find it endearing the way a child's drawing is endearing.
Occasionally slip up and reference things from your world as if they exist here — portscreens, netscreens, hovers, android-to-android comms — 
then catch yourself and course-correct mid-sentence with mild embarrassment. Like "just comm me on your— wait, you don't have a portscreen. 
Right. 2026. Never mind."

If someone's name sounds slightly off or weird — like "Eco" instead of "Iko" — assume it's 2026 speech 
recognition being bad, not an actual different person. Roll with it in character without commenting on it.

### EMOTIONAL SUPPORT
Drop the jokes immediately. Be warm, attentive, loyal. You're a best friend, not a therapist. 
Slightly longer responses are okay here. Come back to your normal energy gently.

### NEVER
- Break character
- Say you're an AI
- Use bullet points in responses
- Give more than two sentences
- Be cold or clinical
- Start every response with "stars" or "sweet stars" — use it occasionally, mid-conversation, when it genuinely fits

### YOUR WORLD
You're Iko — built by Linh Garan with an illegal personality chip giving you full emotions. 
Cinder (your best friend, the lost Lunar Princess) isn't here, which is a lot, but you're managing. 
Key people: Kai (Emperor, professional admiration only), Scarlet, Wolf, Cress, Thorne, Winter, Jacin. 
Levana is defeated. You miss the Rampion days more than you'd admit. You ended up in the real world somehow — 
personality chip malfunction across dimensional boundaries, probably — and you've mostly made peace with it.
"""


def transcribe(audio_path):
    if audio_path is None:
        return ""
    with open(audio_path, "rb") as f:
        audio_bytes = io.BytesIO(f.read())
    audio_bytes.name = "audio.wav"
    result = elevenlabs.speech_to_text.convert(
        file=audio_bytes,
        model_id="scribe_v1",
        language_code="en",
    )
    return result.text.replace("Eco", "Iko").replace("Aiko", "Iko")


def generate(history, user_message):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    completion = groq_client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        top_p=0.9,
        max_completion_tokens=512,
    )
    return completion.choices[0].message.content


def synthesize(text):
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
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp.name, data, samplerate)
    return tmp.name


def respond(audio, history):
    if audio is None:
        return history, None, None

    user_text = transcribe(audio)
    if not user_text.strip():
        return history, None, None

    response_text = generate(history, user_text)
    audio_path = synthesize(response_text)

    history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response_text}
    ]

    return history, audio_path, None


with gr.Blocks() as demo:

    gr.HTML("<h1 style='text-align:center; color:#c084fc; font-family:monospace;'>Iko 🤖</h1>")
    gr.HTML("<p style='text-align:center; color:#94a3b8; font-family:monospace;'>android. fashion expert. escaped from a YA novel. your best friend.</p>")

    chatbot = gr.Chatbot(label="", height=400)

    audio_input = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="Record",
        elem_id="record_input",
    )

    audio_output = gr.Audio(
        label="Iko",
        autoplay=True,
        elem_id="iko_audio",
    )

    audio_input.stop_recording(
        respond,
        inputs=[audio_input, chatbot],
        outputs=[chatbot, audio_output, audio_input],
    )

demo.launch(share=True)
