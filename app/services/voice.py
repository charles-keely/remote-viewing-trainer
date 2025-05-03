import os, io, subprocess, tempfile, logging
import sounddevice as sd
import numpy as np
import openai
import wave
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.warning("OPENAI_API_KEY not found in environment variables. Voice features will not work.")
else:
    openai.api_key = api_key

# ── Text-to-Speech  → returns local file path ───────────────────────────
async def speak(text: str, voice="alloy", model="tts-1") -> str:
    """Convert text to speech using OpenAI's TTS API and play it"""
    if not openai.api_key:
        print("Error: OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        print(f"Would have said: '{text}'")
        return None
    
    try:
        # Use the current OpenAI API format
        client = openai.OpenAI(api_key=api_key)
        
        # Create speech synchronously for simplicity
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        
        # Save the audio to a temporary file
        fd, path = tempfile.mkstemp(suffix=".mp3")
        with os.fdopen(fd, "wb") as f:
            # Use the buffer directly
            response.stream_to_file(path)
        
        # Play the audio with macOS built-in player
        subprocess.run(["afplay", path], check=False)
        return path
    except Exception as e:
        print(f"Error during text-to-speech: {e}")
        print(f"Would have said: '{text}'")
        return None

# ── Record → Whisper STT ────────────────────────────────────────────────
async def listen(seconds: int = 10, sample_rate: int = 16000) -> str:
    """Record audio and transcribe it using OpenAI's Whisper API"""
    if not openai.api_key:
        print("Error: OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        simulated_input = input("🎤 (API key missing) Type what you would say: ")
        return simulated_input.strip()
    
    try:
        print("🎤  Listening…  (stop speaking to finish)")
        recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate,
                           channels=1, dtype="int16")
        sd.wait()
        # trim trailing silence
        samples = np.trim_zeros(recording.flatten(), "b")
        if samples.size == 0:
            return ""
        
        # write wav to buffer
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
            wf.writeframes(samples.tobytes())
        buf.seek(0)
        
        # Create a client with the current API
        client = openai.OpenAI(api_key=api_key)
        
        # Call the Whisper API
        response = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("speech.wav", buf, "audio/wav")
        )
        
        transcribed_text = response.text.strip()
        print(f"Heard: '{transcribed_text}'")
        return transcribed_text
    except Exception as e:
        print(f"Error during speech recognition: {e}")
        fallback_input = input("🎤 (Error in speech recognition) Type what you would say: ")
        return fallback_input.strip() 