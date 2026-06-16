from fastapi import FastAPI, Depends, HTTPException, Header, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Literal
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import os
import logging
import models, database, schemas, user_models
from auth import get_current_user
from worker import analyze_message_task
from hispan_shield_guardian import log_audit
from user_router import router as user_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",") if os.getenv("CORS_ORIGINS") else []
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
if not INTERNAL_API_KEY:
    raise RuntimeError("INTERNAL_API_KEY environment variable is required")

internal_api_key_header = APIKeyHeader(name="X-Internal-API-Key", auto_error=False)


async def verify_internal_api_key(api_key: Optional[str] = Security(internal_api_key_header)):
    if api_key is None or api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing internal API key")
    return api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    audit_info = log_audit()
    logger.info(f"Orchestrator API starting | Audit: {audit_info}")
    models.Base.metadata.create_all(bind=database.engine)
    yield
    logger.info("Orchestrator API shutting down")


app = FastAPI(title="Telegram OSINT Orchestrator", version="1.1.0", lifespan=lifespan)

app.include_router(user_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type", "X-Internal-API-Key"],
    )


@app.post("/ingest/message", response_model=schemas.MessageResponse, dependencies=[Depends(verify_internal_api_key)])
async def ingest_message(msg: schemas.MessageCreate, db: Session = Depends(database.get_db)):
    db_msg = models.Message(
        telegram_id=msg.message_id,
        chat_id=msg.chat_id,
        chat_title=msg.chat_title,
        user_hash=msg.user_handle_hash,
        text=msg.text[:10000],
        timestamp=msg.timestamp,
        lang=msg.lang_detected,
        metadata_json=msg.metadata_extra
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)

    try:
        analyze_message_task.delay(db_msg.id)
    except Exception as e:
        logger.error(f"Failed to enqueue analysis for message {db_msg.id}: {e}")

    return db_msg


@app.get("/cases/{case_id}", response_model=schemas.CaseResponse, dependencies=[Depends(get_current_user)])
async def get_case(case_id: int, db: Session = Depends(database.get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/cases", response_model=List[schemas.CaseResponse], dependencies=[Depends(get_current_user)])
async def list_cases(
    status: Optional[str] = None,
    min_risk: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(database.get_db)
):
    limit = min(limit, 200)
    query = db.query(models.Case)
    if status:
        query = query.filter(models.Case.status == status)
    if min_risk is not None:
        query = query.filter(models.Case.risk_score >= min_risk)
    return query.order_by(models.Case.created_at.desc()).offset(offset).limit(limit).all()


@app.put("/cases/{case_id}", response_model=schemas.CaseResponse, dependencies=[Depends(get_current_user)])
async def update_case(case_id: int, update: schemas.CaseUpdate, db: Session = Depends(database.get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if update.status is not None:
        case.status = update.status
    if update.summary is not None:
        case.summary = update.summary
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


@app.get("/messages/{message_id}", response_model=schemas.MessageResponse, dependencies=[Depends(get_current_user)])
async def get_message(message_id: int, db: Session = Depends(database.get_db)):
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


@app.get("/messages", response_model=List[schemas.MessageResponse], dependencies=[Depends(get_current_user)])
async def list_messages(
    chat_id: Optional[str] = None,
    user_hash: Optional[str] = None,
    min_risk: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(database.get_db)
):
    limit = min(limit, 200)
    query = db.query(models.Message)
    if chat_id:
        query = query.filter(models.Message.chat_id == chat_id)
    if user_hash:
        query = query.filter(models.Message.user_hash == user_hash)
    if min_risk is not None:
        query = query.filter(models.Message.risk_score >= min_risk)
    return query.order_by(models.Message.created_at.desc()).offset(offset).limit(limit).all()


@app.get("/stats/dashboard", dependencies=[Depends(get_current_user)])
async def dashboard_stats(db: Session = Depends(database.get_db)):
    total_messages = db.query(models.Message).count()
    total_cases = db.query(models.Case).count()
    open_cases = db.query(models.Case).filter(models.Case.status == "open").count()
    analyzing_cases = db.query(models.Case).filter(models.Case.status == "analyzing").count()
    analyzed_cases = db.query(models.Case).filter(models.Case.status == "analyzed").count()
    closed_cases = db.query(models.Case).filter(models.Case.status == "closed").count()

    high_risk_messages = db.query(models.Message).filter(models.Message.risk_score >= 12).count()
    medium_risk_messages = db.query(models.Message).filter(
        models.Message.risk_score >= 8, models.Message.risk_score < 12
    ).count()

    return {
        "total_messages": total_messages,
        "total_cases": total_cases,
        "cases_by_status": {
            "open": open_cases,
            "analyzing": analyzing_cases,
            "analyzed": analyzed_cases,
            "closed": closed_cases
        },
        "risk_distribution": {
            "high": high_risk_messages,
            "medium": medium_risk_messages,
            "low": total_messages - high_risk_messages - medium_risk_messages
        }
    }


@app.get("/health", dependencies=[Depends(get_current_user)])
async def health_check(db: Session = Depends(database.get_db)):
    health = {"status": "healthy", "components": {}}
    try:
        db.execute(text("SELECT 1"))
        health["components"]["database"] = "healthy"
    except Exception:
        health["components"]["database"] = "unhealthy"
        health["status"] = "degraded"
    try:
        import redis as redis_lib
        r = redis_lib.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
        r.ping()
        health["components"]["redis"] = "healthy"
    except Exception:
        health["components"]["redis"] = "unhealthy"
        health["status"] = "degraded"
    return health


@app.get("/cases/{case_id}/export/{format}", dependencies=[Depends(get_current_user)])
async def export_case(case_id: int, format: str, db: Session = Depends(database.get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_data = {
        "id": case.id,
        "summary": case.summary or "No summary available.",
        "risk_score": case.risk_score,
        "status": case.status,
        "user_hash": case.user_hash,
        "agent_analysis": case.agent_analysis or {}
    }

    os.makedirs("data", exist_ok=True)

    if format == "pdf":
        from reporting.pdf_generator import generate_pdf_report
        path = f"data/case_{case_id}.pdf"
        generate_pdf_report(case_data, path)
        return FileResponse(path, media_type="application/pdf", filename=f"case_{case_id}.pdf")
    elif format == "docx":
        from reporting.docx_generator import generate_docx_report
        path = f"data/case_{case_id}.docx"
        generate_docx_report(case_data, path)
        return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=f"case_{case_id}.docx")
    else:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'docx'")


@app.get("/")
def read_root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "running", "service": "Telegram OSINT Orchestrator"}
