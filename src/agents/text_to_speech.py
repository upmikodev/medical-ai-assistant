import os
from elevenlabs import generate, play, set_api_key, save

def text_to_speech(text: str, voice: str = "Bella", model: str = "eleven_multilingual_v2"):
    set_api_key(os.getenv("ELEVENLABS_API_KEY"))
    audio = generate(
        text=text,
        voice=voice,
        model=model
    )
    return audio

def save_audio(audio, filename: str):
    save(audio, filename)
