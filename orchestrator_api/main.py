from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import models, database, schemas
import hispan_shield_guardian
from typing import List
import datetime

app = FastAPI(title="Telegram OSINT Orchestrator")

# Create tables
models.Base.metadata.create_all(bind=database.engine)

@app.post("/ingest/message", response_model=schemas.MessageResponse)
async def ingest_message(msg: schemas.MessageCreate, db: Session = Depends(database.get_db)):
    # Store message
    db_msg = models.Message(
        telegram_id=msg.message_id,
        chat_id=msg.chat_id,
        chat_title=msg.chat_title,
        user_hash=msg.user_handle_hash,
        text=msg.text,
        timestamp=msg.timestamp,
        lang=msg.lang_detected,
        metadata_json=msg.metadata_extra
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    
    # Trigger risk scoring asynchronously
    from worker import analyze_message_task
    analyze_message_task.delay(db_msg.id)
    
    return db_msg

@app.get("/cases/{case_id}", response_model=schemas.CaseResponse)
async def get_case(case_id: int, db: Session = Depends(database.get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.get("/")
def read_root():
    return {"status": "running", "version": "1.0.0"}
