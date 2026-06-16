from celery import Celery
import os
import logging
import yaml
from engine.detector import analyze_message
import models, database, agents_connector
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
RULES_DIR = os.getenv("RULES_DIR", "./rules")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
)

LANG_CONFIGS = {}


def load_lang_configs():
    if not os.path.exists(RULES_DIR):
        logger.warning(f"Rules directory {RULES_DIR} not found.")
        return
    for filename in os.listdir(RULES_DIR):
        if filename.endswith(".yaml"):
            lang = filename.split(".")[0]
            with open(os.path.join(RULES_DIR, filename), 'r', encoding='utf-8') as f:
                LANG_CONFIGS[lang] = yaml.safe_load(f)
    logger.info(f"Loaded rules for languages: {list(LANG_CONFIGS.keys())}")


load_lang_configs()


@celery_app.task(
    name="analyze_message",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_max_retries=3,
    retry_jitter=True,
)
def analyze_message_task(message_id: int):
    db = next(database.get_db())
    try:
        msg = db.query(models.Message).filter(models.Message.id == message_id).first()
        if not msg:
            logger.warning(f"Message {message_id} not found")
            return

        lang = msg.lang or "en"
        lang_cfg = LANG_CONFIGS.get(lang, LANG_CONFIGS.get("en", {}))

        result = analyze_message(
            message_id=str(msg.telegram_id),
            user_id=msg.user_hash,
            text=msg.text,
            lang=lang,
            lang_cfg=lang_cfg,
            timestamp=msg.timestamp
        )

        msg.risk_score = result.risk_score
        msg.metadata_json = {
            **(msg.metadata_json or {}),
            "engine_analysis": result.model_dump()
        }
        db.commit()

        if result.risk_score >= 12.0:
            create_case_task.delay(msg.id, result.risk_score)
    except Exception as e:
        logger.error(f"Error analyzing message {message_id}: {e}")
        raise


@celery_app.task(
    name="create_case",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_max_retries=3,
)
def create_case_task(message_id: int, score: float):
    db = next(database.get_db())
    try:
        msg = db.query(models.Message).filter(models.Message.id == message_id).first()
        if not msg:
            return

        six_hours_ago = datetime.utcnow() - timedelta(hours=6)
        existing_case = db.query(models.Case).filter(
            models.Case.user_hash == msg.user_hash,
            models.Case.created_at >= six_hours_ago,
            models.Case.status != "closed"
        ).first()

        if existing_case:
            if score > existing_case.risk_score:
                existing_case.risk_score = score
            db.commit()
        else:
            new_case = models.Case(
                user_hash=msg.user_hash,
                risk_score=score,
                initial_message_id=msg.id,
                status="open"
            )
            db.add(new_case)
            db.commit()
            db.refresh(new_case)
            agents_connector.run_agent_analysis.delay(new_case.id)
    except Exception as e:
        logger.error(f"Error creating case for message {message_id}: {e}")
        raise
