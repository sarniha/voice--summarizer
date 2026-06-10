from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.transcription import transcribe_audio
from app.services.summarization import summarize_transcript

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",  
                 "https://voice-summarizer-five.vercel.app", 
                 "*", 
],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "server is running"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.endswith((".mp3", ".wav", ".m4a", ".webm", ".ogg")):
        raise HTTPException(status_code=400, detail="Invalid file type. Upload an audio file.")
    
    try:
        contents = await file.read()
        transcript = await transcribe_audio(contents, file.filename)
        summary = await summarize_transcript(transcript)
        return {
            "filename": file.filename,
            "transcript": transcript,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))