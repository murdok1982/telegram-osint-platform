from celery import Celery
from celery.schedules import crontab
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import func

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("beat_tasks", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.beat_schedule = {
    "aggregate-user-risk-every-30min": {
        "task": "aggregate_user_risk",
        "schedule": 1800.0,
    },
    "cleanup-old-messages-daily": {
        "task": "cleanup_old_messages",
        "schedule": crontab(hour=3, minute=0),
    },
    "check-stale-cases-hourly": {
        "task": "check_stale_cases",
        "schedule": 3600.0,
    },
}

celery_app.conf.timezone = "UTC"


@celery_app.task(name="aggregate_user_risk")
def aggregate_user_risk():
    import models, database
    from engine.correlator import aggregate_by_user, risk_level_from_score
    from engine.models import MessageResult, Match

    db = next(database.get_db())
    try:
        window_start = datetime.utcnow() - timedelta(hours=3)
        recent_messages = db.query(models.Message).filter(
            models.Message.created_at >= window_start,
            models.Message.risk_score > 0
        ).all()

        if not recent_messages:
            logger.info("No recent messages to aggregate")
            return {"aggregated": 0}

        results = []
        for msg in recent_messages:
            results.append(MessageResult(
                message_id=str(msg.telegram_id),
                user_id=msg.user_hash,
                language=msg.lang or "unknown",
                raw_text=msg.text or "",
                normalized_text=msg.text or "",
                timestamp=msg.timestamp or msg.created_at,
                risk_score=msg.risk_score,
                risk_level=risk_level_from_score(msg.risk_score),
                matches=[],
                crypto_signals={},
                notes=[]
            ))

        aggs = aggregate_by_user(results, window_minutes=180)

        for agg in aggs:
            if agg.peak_risk >= 12 or agg.cumulative_risk >= 30:
                existing = db.query(models.Case).filter(
                    models.Case.user_hash == agg.user_id,
                    models.Case.status.in_(["open", "analyzing"]),
                    models.Case.created_at >= window_start
                ).first()

                if not existing:
                    first_msg = db.query(models.Message).filter(
                        models.Message.user_hash == agg.user_id,
                        models.Message.created_at >= window_start
                    ).order_by(models.Message.created_at).first()

                    if first_msg:
                        new_case = models.Case(
                            user_hash=agg.user_id,
                            risk_score=agg.peak_risk,
                            initial_message_id=first_msg.id,
                            status="open",
                            summary=f"Aggregate risk: {agg.total_messages} messages, peak={agg.peak_risk}, cumulative={agg.cumulative_risk}, flags={agg.flags}"
                        )
                        db.add(new_case)

        db.commit()
        logger.info(f"Aggregated risk for {len(aggs)} users")
        return {"aggregated": len(aggs)}
    except Exception as e:
        logger.error(f"Error in aggregate_user_risk: {e}")
        raise
    finally:
        db.close()


@celery_app.task(name="cleanup_old_messages")
def cleanup_old_messages():
    import models, database

    db = next(database.get_db())
    try:
        cutoff = datetime.utcnow() - timedelta(days=90)
        count = db.query(models.Message).filter(models.Message.created_at < cutoff).count()
        if count > 0:
            db.query(models.Message).filter(models.Message.created_at < cutoff).delete()
            db.commit()
        logger.info(f"Cleaned up {count} old messages (older than 90 days)")
        return {"deleted": count}
    except Exception as e:
        logger.error(f"Error in cleanup_old_messages: {e}")
        raise
    finally:
        db.close()


@celery_app.task(name="check_stale_cases")
def check_stale_cases():
    import models, database

    db = next(database.get_db())
    try:
        stale_threshold = datetime.utcnow() - timedelta(hours=24)
        stale_cases = db.query(models.Case).filter(
            models.Case.status == "analyzing",
            models.Case.updated_at < stale_threshold
        ).all()

        for case in stale_cases:
            case.status = "error"
            case.summary = (case.summary or "") + " [Auto-flagged: analysis stalled >24h]"

        db.commit()
        if stale_cases:
            logger.warning(f"Flagged {len(stale_cases)} stale cases")
        return {"flagged": len(stale_cases)}
    except Exception as e:
        logger.error(f"Error in check_stale_cases: {e}")
        raise
    finally:
        db.close()
