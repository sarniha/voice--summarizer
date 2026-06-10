import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    transcript = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=(filename, file_bytes, "audio/mpeg"),
    )
    return transcript.text