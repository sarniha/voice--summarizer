from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.services.transcription import transcribe_audio
from app.services.summarization import summarize_transcript
from app.database import get_db, create_tables, Note
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    create_tables()

@app.get("/")
def health_check():
    return {"status": "server is running"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".mp3", ".wav", ".m4a", ".webm", ".ogg")):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = await file.read()
        transcript = await transcribe_audio(contents, file.filename)
        summary = await summarize_transcript(transcript)

        # save to database
        note = Note(
            filename=file.filename,
            transcript=transcript,
            summary=summary["summary"],
            action_items=json.dumps(summary["action_items"]),
            key_points=json.dumps(summary["key_points"])
        )
        db.add(note)
        db.commit()
        db.refresh(note)

        return {
            "id": note.id,
            "filename": note.filename,
            "transcript": transcript,
            "summary": summary,
            "created_at": note.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    notes = db.query(Note).order_by(Note.created_at.desc()).all()
    return [
        {
            "id": note.id,
            "filename": note.filename,
            "summary": note.summary,
            "action_items": json.loads(note.action_items),
            "key_points": json.loads(note.key_points),
            "created_at": note.created_at
        }
        for note in notes
    ]

@app.get("/history/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "id": note.id,
        "filename": note.filename,
        "transcript": note.transcript,
        "summary": note.summary,
        "action_items": json.loads(note.action_items),
        "key_points": json.loads(note.key_points),
        "created_at": note.created_at
    }
@app.delete("/history/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": f"Note {note_id} deleted"}