from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class MessageCreate(BaseModel):
    message_id: str
    chat_id: str
    chat_title: Optional[str] = None
    user_handle_hash: str
    text: str = Field(..., max_length=10000)
    timestamp: datetime
    lang_detected: Optional[str] = None
    metadata_extra: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: int
    telegram_id: str
    risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class CaseResponse(BaseModel):
    id: int
    status: str
    risk_score: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseUpdate(BaseModel):
    status: Optional[Literal["open", "analyzing", "analyzed", "closed", "error"]] = None
    summary: Optional[str] = Field(None, max_length=5000)
