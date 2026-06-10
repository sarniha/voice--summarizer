import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def summarize_transcript(transcript: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a JSON-only response bot. You must always respond with valid JSON and nothing else. No explanation, no markdown, no code blocks. Just raw JSON."
            },
            {
                "role": "user",
                "content": f"""Analyze this transcript and return a JSON object with exactly these three fields:
{{
    "summary": "2-3 sentence summary",
    "action_items": ["item1", "item2"],
    "key_points": ["point1", "point2"]
}}

Transcript: {transcript}"""
            }
        ],
        temperature=0,  # makes output deterministic, less creative = more reliable JSON
    )

    raw = response.choices[0].message.content.strip()
    
    # strip markdown code blocks if model wraps in them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())