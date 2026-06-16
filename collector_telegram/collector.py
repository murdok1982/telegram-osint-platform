from telethon import TelegramClient, events
import os
import hashlib
import logging
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("telegram_collector")

API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator_api:8000")
SALT = os.getenv("HASH_SALT")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

if not API_ID or not API_HASH:
    logger.error("TG_API_ID and TG_API_HASH are required")
    raise RuntimeError("Missing Telegram API credentials")

if not SALT:
    logger.error("HASH_SALT is required for user pseudonymization")
    raise RuntimeError("HASH_SALT environment variable is required. Cannot start without it.")

if not INTERNAL_API_KEY:
    logger.error("INTERNAL_API_KEY is required for service-to-service authentication")
    raise RuntimeError("INTERNAL_API_KEY environment variable is required. Cannot start without it.")

MONITORED_CHATS_RAW = os.getenv("MONITORED_CHATS", "")
MONITORED_CHATS = set()
if MONITORED_CHATS_RAW.strip():
    MONITORED_CHATS = {int(c.strip()) for c in MONITORED_CHATS_RAW.split(",") if c.strip().lstrip("-").isdigit()}

os.makedirs("data", exist_ok=True)
client = TelegramClient('data/collector_session', int(API_ID), API_HASH)


def pseudonymize_user(user_id: int) -> str:
    if not user_id:
        return "anonymous"
    return hashlib.sha256(f"{user_id}{SALT}".encode()).hexdigest()


@client.on(events.NewMessage)
async def message_handler(event):
    if not (event.is_group or event.is_channel):
        return

    if MONITORED_CHATS and event.chat_id not in MONITORED_CHATS:
        return

    chat = await event.get_chat()
    user_hash = pseudonymize_user(event.sender_id)

    payload = {
        "message_id": str(event.id),
        "chat_id": str(event.chat_id),
        "chat_title": getattr(chat, 'title', None),
        "user_handle_hash": user_hash,
        "text": event.message.message or "",
        "timestamp": event.date.isoformat(),
        "lang_detected": None,
        "metadata_extra": {
            "reply_to": event.reply_to_msg_id,
            "forwarded_from": str(event.fwd_from) if event.fwd_from else None,
            "entities": [ent.to_dict() for ent in (event.entities or [])]
        }
    }

    headers = {"X-Internal-API-Key": INTERNAL_API_KEY}

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        try:
            r = await http_client.post(
                f"{ORCHESTRATOR_URL}/ingest/message",
                json=payload,
                headers=headers
            )
            if r.status_code == 200:
                logger.info(f"Message ingested: {event.id} from chat {event.chat_id}")
            else:
                logger.warning(f"Ingest failed ({r.status_code}): {event.id}")
        except httpx.ConnectError:
            logger.error(f"Cannot connect to orchestrator at {ORCHESTRATOR_URL}")
        except Exception as e:
            logger.error(f"Error sending message to orchestrator: {e}")


if __name__ == "__main__":
    logger.info("Starting Telegram Collector...")
    if MONITORED_CHATS:
        logger.info(f"Monitoring {len(MONITORED_CHATS)} specific chats")
    else:
        logger.info("Monitoring ALL groups and channels (no filter set)")
    client.start()
    client.run_until_disconnected()
